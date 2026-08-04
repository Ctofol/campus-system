import asyncio
from datetime import datetime, timedelta

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models, schemas
from app.routers import student, teacher
from app.services.health_request_service import refresh_expired_health_requests


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


def _user(db, role, name):
    row = models.User(role=role, name=name, password_hash="test")
    db.add(row)
    db.commit()
    return row


def _leave_input():
    now = datetime.utcnow()
    return schemas.HealthRequestCreate(
        type="leave",
        reason="身体不适",
        start_date=now + timedelta(hours=1),
        end_date=now + timedelta(days=1),
    )


def test_student_can_cancel_only_own_pending_request(db):
    owner = _user(db, "student", "申请学生")
    other = _user(db, "student", "其他学生")
    created = student.create_health_request(_leave_input(), owner, db)

    with pytest.raises(HTTPException) as exc_info:
        student.cancel_health_request(created["id"], other, db)
    assert exc_info.value.status_code == 404

    assert student.cancel_health_request(created["id"], owner, db) == {"success": True}
    row = db.get(models.HealthRequest, created["id"])
    assert row.status == "cancelled"
    assert row.cancelled_at is not None
    with pytest.raises(HTTPException) as exc_info:
        student.cancel_health_request(created["id"], owner, db)
    assert exc_info.value.status_code == 409


def test_teacher_cannot_review_unmanaged_or_repeat_review(db, monkeypatch):
    reviewer = _user(db, "teacher", "教师")
    managed = _user(db, "student", "管辖学生")
    outside = _user(db, "student", "非管辖学生")
    managed_request = student.create_health_request(_leave_input(), managed, db)
    outside_request = models.HealthRequest(student_id=outside.id, type="injury", reason="扭伤", status="pending")
    db.add(outside_request)
    db.commit()

    async def managed_query(_teacher, session):
        return session.query(models.User).filter(models.User.id == managed.id)

    monkeypatch.setattr(teacher, "get_managed_students_query", managed_query)
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(teacher.review_health_request(outside_request.id, {"status": "approved"}, reviewer, db))
    assert exc_info.value.status_code == 403

    asyncio.run(teacher.review_health_request(managed_request["id"], {"status": "approved", "comment": "同意"}, reviewer, db))
    row = db.get(models.HealthRequest, managed_request["id"])
    assert row.reviewed_by == reviewer.id
    assert row.review_comment == "同意"
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(teacher.review_health_request(managed_request["id"], {"status": "rejected"}, reviewer, db))
    assert exc_info.value.status_code == 409


def test_expired_leave_ends_and_restores_health_status(db):
    student_user = _user(db, "student", "学生")
    now = datetime.utcnow()
    row = models.HealthRequest(
        student_id=student_user.id,
        type="leave",
        reason="短期请假",
        status="approved",
        start_date=now - timedelta(days=2),
        end_date=now - timedelta(minutes=1),
        reviewed_at=now - timedelta(days=2),
    )
    student_user.health_status = "leave"
    student_user.abnormal_reason = row.reason
    db.add(row)
    db.commit()

    assert refresh_expired_health_requests(db, student_id=student_user.id, now=now) == 1
    db.refresh(row)
    db.refresh(student_user)
    assert row.status == "ended"
    assert row.ended_at == now
    assert student_user.health_status == "normal"
    assert student_user.abnormal_reason is None
