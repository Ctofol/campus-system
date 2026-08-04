import asyncio
from datetime import datetime

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models, schemas
from app.routers import activity, teacher


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


def _invalid_activity(db, student):
    now = datetime.utcnow()
    row = models.Activity(
        user_id=student.id,
        type="run",
        source="free",
        status="finished",
        started_at=now,
        ended_at=now,
        is_valid=False,
        fail_reason="配速异常",
    )
    db.add(row)
    db.commit()
    return row


def test_student_can_appeal_only_own_invalid_activity_once(db):
    owner = _user(db, "student", "学生")
    other = _user(db, "student", "其他学生")
    invalid = _invalid_activity(db, owner)

    with pytest.raises(HTTPException) as exc_info:
        activity.create_activity_appeal(invalid.id, schemas.ActivityAppealCreate(reason="请老师重新核查"), other, db)
    assert exc_info.value.status_code == 404

    created = activity.create_activity_appeal(
        invalid.id, schemas.ActivityAppealCreate(reason="定位短时漂移，请重新核查"), owner, db
    )
    assert created["status"] == "pending"
    with pytest.raises(HTTPException) as exc_info:
        activity.create_activity_appeal(
            invalid.id, schemas.ActivityAppealCreate(reason="再次提交申诉"), owner, db
        )
    assert exc_info.value.status_code == 409


def test_teacher_review_requires_management_and_updates_activity(db, monkeypatch):
    reviewer = _user(db, "teacher", "教师")
    student_user = _user(db, "student", "管辖学生")
    invalid = _invalid_activity(db, student_user)
    created = activity.create_activity_appeal(
        invalid.id, schemas.ActivityAppealCreate(reason="定位异常，请人工核查"), student_user, db
    )

    async def no_students(_teacher, session):
        return session.query(models.User).filter(models.User.id == -1)

    monkeypatch.setattr(teacher, "get_managed_students_query", no_students)
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(teacher.review_activity_appeal(
            created["id"], schemas.ActivityAppealReview(status="approved"), reviewer, db
        ))
    assert exc_info.value.status_code == 404

    async def managed_students(_teacher, session):
        return session.query(models.User).filter(models.User.id == student_user.id)

    monkeypatch.setattr(teacher, "get_managed_students_query", managed_students)
    asyncio.run(teacher.review_activity_appeal(
        created["id"], schemas.ActivityAppealReview(status="approved", comment="轨迹证据有效"), reviewer, db
    ))
    db.refresh(invalid)
    appeal = db.get(models.ActivityAppeal, created["id"])
    assert invalid.is_valid is True
    assert invalid.fail_reason is None
    assert appeal.status == "approved"
    assert appeal.review_comment == "轨迹证据有效"
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(teacher.review_activity_appeal(
            created["id"], schemas.ActivityAppealReview(status="rejected"), reviewer, db
        ))
    assert exc_info.value.status_code == 409
