"""上传目录只读盘点；不移动、修改或删除任何文件。"""

from __future__ import annotations

import os
import re
from collections import Counter
from pathlib import Path

from sqlalchemy.orm import Session

from .. import database, models


_UPLOAD_PATH_PATTERN = re.compile(r"/uploads/[^\s\"']+")


def get_upload_root() -> Path:
    container_root = Path("/app/uploads")
    return container_root if container_root.exists() else Path(database.PROJECT_ROOT) / "uploads"


def collect_upload_references(db: Session) -> set[str]:
    references: set[str] = set()
    fields = (
        (models.User, "avatar_url"),
        (models.User, "header_bg_url"),
        (models.StudentFaceProfile, "image_url"),
        (models.ActivityMetrics, "video_url"),
        (models.Task, "video_url"),
        (models.Course, "cover_url"),
        (models.CourseContent, "content_url"),
        (models.RunGroup, "avatar"),
        (models.RunGroupActivity, "cover_image"),
    )
    for model, field_name in fields:
        column = getattr(model, field_name)
        for (value,) in db.query(column).filter(column.isnot(None)).all():
            if isinstance(value, str) and value.startswith("/uploads/"):
                references.add(value)

    # 活动证据可能是路径，也可能是包含路径的 JSON 文本。
    for (value,) in db.query(models.ActivityEvidence.data_ref).filter(
        models.ActivityEvidence.data_ref.isnot(None)
    ).all():
        if isinstance(value, str):
            references.update(_UPLOAD_PATH_PATTERN.findall(value))
    return references


def scan_upload_usage(root: Path, references: set[str], *, candidate_limit: int = 50) -> dict:
    files: list[tuple[str, int]] = []
    if root.is_dir():
        for base, _dirs, names in os.walk(root):
            for name in names:
                if name == ".gitkeep":
                    continue
                file_path = Path(base) / name
                try:
                    size = file_path.stat().st_size
                except OSError:
                    continue
                relative = "/uploads/" + file_path.relative_to(root).as_posix()
                files.append((relative, size))

    existing_paths = {path for path, _size in files}
    unreferenced = sorted(
        ((path, size) for path, size in files if path not in references),
        key=lambda item: item[1],
        reverse=True,
    )
    by_month = Counter(
        path.split("/")[2] if len(path.split("/")) > 3 else "未分类"
        for path, _size in files
    )
    return {
        "status": "ok" if root.is_dir() else "missing",
        "total_files": len(files),
        "total_bytes": sum(size for _path, size in files),
        "referenced_files": len(existing_paths & references),
        "unreferenced_files": len(unreferenced),
        "missing_references": len(references - existing_paths),
        "by_month": dict(sorted(by_month.items())),
        "candidates": [
            {"path": path, "size_bytes": size}
            for path, size in unreferenced[: max(candidate_limit, 0)]
        ],
    }


def build_upload_usage_report(db: Session, *, candidate_limit: int = 50) -> dict:
    return scan_upload_usage(
        get_upload_root(),
        collect_upload_references(db),
        candidate_limit=candidate_limit,
    )
