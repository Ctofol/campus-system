from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models, schemas
from app.routers import activity, admin


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


def test_mock_profile_import_is_hidden_in_production(db, monkeypatch):
    monkeypatch.setattr(admin.config, "APP_ENV", "production")
    with pytest.raises(HTTPException) as exc_info:
        admin.mock_import_student_profiles([], db, SimpleNamespace(id=1, role="admin"))
    assert exc_info.value.status_code == 404


def test_checkpoint_checkin_is_persisted_and_recent_duplicate_is_reused(db):
    student = _user(db, "student", "学生")
    checkpoint = models.Checkpoint(name="操场入口", latitude=23.1, longitude=113.3, radius=50)
    db.add(checkpoint)
    db.commit()
    request = schemas.CheckInRequest(lat=23.1, lng=113.3, checkpoint_id=checkpoint.id)

    first = activity.check_in(request, student, db)
    second = activity.check_in(request, student, db)
    assert first["success"] is True and first["duplicate"] is False
    assert second["success"] is True and second["duplicate"] is True
    assert second["visit_id"] == first["visit_id"]
    assert db.query(models.CheckpointVisit).count() == 1

    history = activity.list_my_checkins(1, 20, student, db)
    assert history["total"] == 1
    assert history["items"][0]["checkpoint_name"] == "操场入口"


def test_checkpoint_rejects_non_student_and_does_not_store_out_of_range(db):
    teacher = _user(db, "teacher", "教师")
    student = _user(db, "student", "学生")
    checkpoint = models.Checkpoint(name="操场入口", latitude=23.1, longitude=113.3, radius=20)
    db.add(checkpoint)
    db.commit()
    request = schemas.CheckInRequest(lat=24.1, lng=114.3, checkpoint_id=checkpoint.id)

    with pytest.raises(HTTPException) as exc_info:
        activity.check_in(request, teacher, db)
    assert exc_info.value.status_code == 403
    assert activity.check_in(request, student, db)["success"] is False
    assert db.query(models.CheckpointVisit).count() == 0
