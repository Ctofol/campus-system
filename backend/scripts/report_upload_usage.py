"""生成上传文件使用情况报告；只读，不删除任何文件。"""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app import database  # noqa: E402
from app.services.storage_report import build_upload_usage_report  # noqa: E402


def main() -> None:
    db = database.SessionLocal()
    try:
        report = build_upload_usage_report(db, candidate_limit=100)
        print(f"文件总数: {report['total_files']}")
        print(f"占用空间(MB): {report['total_bytes'] / 1024 / 1024:.2f}")
        print(f"已引用文件数: {report['referenced_files']}")
        print(f"未引用候选数: {report['unreferenced_files']}")
        print(f"引用存在但文件缺失数: {report['missing_references']}")
        print(f"按目录统计: {report['by_month']}")
        for item in report["candidates"]:
            print(f"候选清理: {item['path']} ({item['size_bytes'] / 1024 / 1024:.2f} MB)")
    finally:
        db.close()


if __name__ == "__main__":
    main()
