import io

import pytest
from fastapi import HTTPException

from app.routers.upload import save_upload_with_limit


class _Upload:
    def __init__(self, content: bytes):
        self.file = io.BytesIO(content)


def test_save_upload_enforces_actual_stream_size(tmp_path):
    target = tmp_path / "too-large.bin"

    with pytest.raises(HTTPException) as exc:
        save_upload_with_limit(_Upload(b"12345"), str(target), max_size=4)

    assert exc.value.status_code == 413
    assert not target.exists()


def test_save_upload_returns_actual_size(tmp_path):
    target = tmp_path / "ok.bin"

    size = save_upload_with_limit(_Upload(b"1234"), str(target), max_size=4)

    assert size == 4
    assert target.read_bytes() == b"1234"
