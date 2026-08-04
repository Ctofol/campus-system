import asyncio

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models, schemas
from app.routers import notification_campaigns, notifications
from app.services.notification_campaign_service import (
    campaign_stats,
    create_campaign,
    preview_users,
    resolve_admin_recipients,
    resolve_teacher_recipients,
)
from app.services.notification_service import create_notification, validate_notification


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    models.Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def _user(db, role, name, *, student_id=None, class_id=None, subject=None):
    row = models.User(
        role=role,
        name=name,
        phone=None,
        password_hash="test-only",
        student_id=student_id,
        class_id=class_id,
        subject=subject,
    )
    db.add(row)
    db.flush()
    return row


def test_user_can_only_read_and_modify_own_notifications(db):
    first = _user(db, "student", "学生甲", student_id="S001")
    second = _user(db, "student", "学生乙", student_id="S002")
    note = create_notification(db, first.id, "测试通知", "正文")
    db.commit()

    assert notifications.get_my_notification(note.id, first, db)["id"] == note.id
    with pytest.raises(HTTPException) as exc_info:
        notifications.get_my_notification(note.id, second, db)
    assert exc_info.value.status_code == 404
    with pytest.raises(HTTPException) as exc_info:
        notifications.mark_notification_read(note.id, second, db)
    assert exc_info.value.status_code == 404

    notifications.mark_notification_read(note.id, first, db)
    db.refresh(note)
    assert note.is_read is True
    assert note.read_at is not None
    assert notifications.my_notification_unread_count(first, db)["count"] == 0


def test_event_key_deduplicates_per_recipient(db):
    first = _user(db, "student", "学生甲", student_id="S011")
    second = _user(db, "student", "学生乙", student_id="S012")
    assert create_notification(db, first.id, "提醒", event_key="task:1:2026-08-03") is not None
    db.flush()
    assert create_notification(db, first.id, "提醒", event_key="task:1:2026-08-03") is None
    assert create_notification(db, second.id, "提醒", event_key="task:1:2026-08-03") is not None


def test_admin_preview_matches_send_and_recipient_ids_are_deduplicated(db):
    admin = _user(db, "admin", "管理员")
    first = _user(db, "student", "学生甲", student_id="S021")
    second = _user(db, "student", "学生乙", student_id="S022")
    _user(db, "teacher", "教师甲")
    db.commit()

    users = resolve_admin_recipients(db, "users", [first.id, first.id, second.id])
    preview = preview_users(users)
    campaign = create_campaign(
        db,
        sender=admin,
        users=users,
        title="精准通知",
        body="请及时查看",
        ntype="system",
        target_type="users",
        target_values=[first.id, first.id, second.id],
    )
    db.commit()
    stats = campaign_stats(db, campaign)
    assert preview["recipient_count"] == stats["recipient_count"] == 2
    assert db.query(models.UserNotification).filter_by(campaign_id=campaign.id).count() == 2


def test_invalid_or_empty_admin_target_creates_nothing(db):
    admin = _user(db, "admin", "管理员")
    _user(db, "student", "学生甲", student_id="S031")
    db.commit()
    before = db.query(models.UserNotification).count()

    with pytest.raises(ValueError, match="发送范围"):
        resolve_admin_recipients(db, "unknown", [])
    with pytest.raises(ValueError, match="请选择班级"):
        resolve_admin_recipients(db, "classes", [])
    with pytest.raises(ValueError, match="没有可接收"):
        create_campaign(
            db,
            sender=admin,
            users=[],
            title="空范围",
            body="正文",
            ntype="system",
            target_type="users",
            target_values=[],
        )
    assert db.query(models.UserNotification).count() == before


def test_teacher_cannot_send_to_unmanaged_student(db):
    teacher = _user(db, "teacher", "教师甲")
    managed = _user(db, "student", "管辖学生", student_id="S041")
    outside = _user(db, "student", "其他学生", student_id="S042")
    db.add(models.TeacherStudent(teacher_id=teacher.id, student_user_id=managed.id))
    db.commit()

    assert [row.id for row in asyncio.run(resolve_teacher_recipients(db, teacher, "users", [managed.id]))] == [managed.id]
    with pytest.raises(ValueError, match="非本人管辖学生"):
        asyncio.run(resolve_teacher_recipients(db, teacher, "users", [managed.id, outside.id]))
    with pytest.raises(ValueError, match="非本人管辖学生"):
        asyncio.run(resolve_teacher_recipients(db, teacher, "users", [outside.id]))
    assert db.query(models.UserNotification).count() == 0


def test_campaign_read_statistics_and_mark_all_are_consistent(db):
    admin = _user(db, "admin", "管理员")
    first = _user(db, "student", "学生甲", student_id="S051")
    second = _user(db, "student", "学生乙", student_id="S052")
    campaign = create_campaign(
        db,
        sender=admin,
        users=[first, second],
        title="统计通知",
        body="正文",
        ntype="system",
        target_type="students",
        target_values=[],
    )
    db.commit()
    first_note = db.query(models.UserNotification).filter_by(campaign_id=campaign.id, user_id=first.id).one()
    notifications.mark_notification_read(first_note.id, first, db)
    stats = campaign_stats(db, campaign)
    assert (stats["read_count"], stats["unread_count"], stats["read_rate"]) == (1, 1, 50.0)

    notifications.mark_all_notifications_read(second, db)
    stats = campaign_stats(db, campaign)
    assert (stats["read_count"], stats["unread_count"], stats["read_rate"]) == (2, 0, 100.0)


def test_only_allowlisted_actions_and_bounded_content_are_accepted():
    with pytest.raises(ValueError, match="跳转类型"):
        validate_notification("标题", "正文", "system", "external_url", {"url": "https://example.com"})
    with pytest.raises(ValueError, match="标题不能超过"):
        validate_notification("超" * 61, "正文")
    with pytest.raises(ValueError, match="内容不能超过"):
        validate_notification("标题", "长" * 501)


def test_student_and_teacher_share_the_same_notification_schema(db):
    student = _user(db, "student", "学生甲", student_id="S061")
    teacher = _user(db, "teacher", "教师甲")
    first = create_notification(db, student.id, "学生通知", "正文", sender_user_id=teacher.id)
    second = create_notification(db, teacher.id, "教师通知", "正文", sender_user_id=student.id)
    db.commit()
    student_data = schemas.UserNotificationOut.model_validate(first).model_dump().keys()
    teacher_data = schemas.UserNotificationOut.model_validate(second).model_dump().keys()
    assert student_data == teacher_data
