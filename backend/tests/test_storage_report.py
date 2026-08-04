from pathlib import Path

from app.services.storage_report import scan_upload_usage


def _write(path: Path, size: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"x" * size)


def test_scan_upload_usage_is_read_only_and_classifies_files(tmp_path):
    referenced = tmp_path / "2026-07" / "kept.jpg"
    candidate = tmp_path / "2026-06" / "unused.mp4"
    _write(referenced, 5)
    _write(candidate, 12)
    _write(tmp_path / ".gitkeep", 0)

    result = scan_upload_usage(
        tmp_path,
        {"/uploads/2026-07/kept.jpg", "/uploads/missing.jpg"},
    )

    assert result["total_files"] == 2
    assert result["total_bytes"] == 17
    assert result["referenced_files"] == 1
    assert result["unreferenced_files"] == 1
    assert result["missing_references"] == 1
    assert result["candidates"] == [
        {"path": "/uploads/2026-06/unused.mp4", "size_bytes": 12}
    ]
    assert referenced.exists()
    assert candidate.exists()


def test_scan_upload_usage_reports_missing_directory(tmp_path):
    result = scan_upload_usage(tmp_path / "not-created", set())

    assert result["status"] == "missing"
    assert result["total_files"] == 0
