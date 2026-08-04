import asyncio
import io

import pandas as pd
import pytest
from fastapi import HTTPException, UploadFile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models
from app.routers import admin


@pytest.fixture()
def db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    models.Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def _admin(db):
    row = models.User(role="admin", name="管理员", password_hash="test")
    db.add(row)
    db.commit()
    return row


def _excel_upload(rows, filename="students.xlsx"):
    stream = io.BytesIO()
    pd.DataFrame(rows).to_excel(stream, index=False, engine="openpyxl")
    stream.seek(0)
    return UploadFile(filename=filename, file=stream)


def test_preview_is_read_only_and_rejects_duplicate_rows(db):
    actor = _admin(db)
    upload = _excel_upload([
        {"学号": "2026001", "姓名": "张三", "性别": "男", "所属班级名称": "一班", "专业/课程": "体育"},
        {"学号": "2026001", "姓名": "李四", "性别": "女", "所属班级名称": "一班", "专业/课程": "体育"},
    ])
    result = asyncio.run(admin.preview_import("student", upload, db, actor))
    assert result["total"] == 2
    assert result["invalid"] == 1
    assert result["can_import"] is False
    assert db.query(models.User).filter(models.User.role == "student").count() == 0
    assert db.query(models.Major).count() == 0


def test_student_import_creates_batch_and_can_safely_rollback(db):
    actor = _admin(db)
    rows = [{"学号": "2026002", "姓名": "王五", "性别": "男", "所属班级名称": "二班", "专业/课程": "体育"}]
    result = asyncio.run(admin.import_students(_excel_upload(rows), db, actor))
    assert result["success"] == 1
    batch = db.get(models.ImportBatch, result["batch_id"])
    assert batch.status == "completed"
    assert db.query(models.User).filter(models.User.student_id == "2026002").count() == 1

    rollback = admin.rollback_import_batch(batch.id, db, actor)
    assert rollback["deleted_users"] == 1
    assert rollback["deleted_profiles"] == 1
    assert db.query(models.User).filter(models.User.student_id == "2026002").count() == 0
    assert db.query(models.StudentProfile).filter_by(student_id="2026002").count() == 0


def test_rollback_is_blocked_after_imported_user_has_business_data(db):
    actor = _admin(db)
    rows = [{"学号": "2026003", "姓名": "赵六", "性别": "女", "所属班级名称": "三班", "专业/课程": "体育"}]
    result = asyncio.run(admin.import_students(_excel_upload(rows), db, actor))
    user = db.query(models.User).filter(models.User.student_id == "2026003").first()
    db.add(models.HealthRequest(student_id=user.id, type="injury", reason="测试", status="pending"))
    db.commit()
    with pytest.raises(HTTPException) as exc_info:
        admin.rollback_import_batch(result["batch_id"], db, actor)
    assert exc_info.value.status_code == 409
    assert db.query(models.User).filter(models.User.id == user.id).count() == 1
