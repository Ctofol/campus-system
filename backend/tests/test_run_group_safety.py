import asyncio
from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models
from app.routers import run_groups


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


def _user(db, name):
    row = models.User(role="student", name=name, password_hash="test")
    db.add(row)
    db.commit()
    return row


def _group_with_activity(db, creator, quota=1):
    group = models.RunGroup(name="安全跑团", creator_id=creator.id, member_count=1, status="active")
    db.add(group)
    db.flush()
    db.add(models.RunGroupMember(group_id=group.id, user_id=creator.id, role="creator"))
    event = models.RunGroupActivity(
        group_id=group.id,
        title="周末训练",
        activity_time=datetime.utcnow() + timedelta(days=1),
        total_quota=quota,
        apply_count=0,
        status="upcoming",
        created_by=creator.id,
    )
    db.add(event)
    db.commit()
    return group, event


def test_activity_capacity_and_duplicate_application_are_protected(db):
    creator = _user(db, "团长")
    first_student = _user(db, "学生甲")
    second_student = _user(db, "学生乙")
    _group, event = _group_with_activity(db, creator, quota=1)

    first = asyncio.run(run_groups.apply_activity(event.id, first_student, db))
    duplicate = asyncio.run(run_groups.apply_activity(event.id, first_student, db))
    full = asyncio.run(run_groups.apply_activity(event.id, second_student, db))
    assert first["applyStatus"] is True
    assert duplicate["applyStatus"] is False
    assert full == {"applyStatus": False, "message": "活动名额已满"}
    db.refresh(event)
    assert event.apply_count == 1
    assert db.query(models.RunGroupActivityApplication).count() == 1


def test_dissolving_group_preserves_members_activities_and_applications(db):
    creator = _user(db, "团长")
    applicant = _user(db, "报名学生")
    group, event = _group_with_activity(db, creator, quota=3)
    asyncio.run(run_groups.apply_activity(event.id, applicant, db))

    result = asyncio.run(run_groups.delete_current_run_group(group.id, creator, db))
    assert result["success"] is True
    db.refresh(group)
    db.refresh(event)
    assert group.status == "dissolved"
    assert group.archived_at is not None
    assert event.status == "finished"
    assert db.query(models.RunGroupMember).filter_by(group_id=group.id).count() == 1
    assert db.query(models.RunGroupActivityApplication).filter_by(activity_id=event.id).count() == 1
    assert asyncio.run(run_groups.get_run_groups(1, 20, applicant, db)) == []
    assert asyncio.run(run_groups.get_my_run_groups(creator, db)) == []
