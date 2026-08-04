"""通知批次、目标解析与阅读统计。"""

import json
from typing import Iterable

from sqlalchemy.orm import Session

from .. import models
from .notification_service import create_notifications, validate_notification
from .teacher_service import get_managed_students_query


ADMIN_TARGETS = {"all", "students", "teachers", "classes", "majors", "subjects", "users"}
TEACHER_TARGETS = {"all_managed", "classes", "subjects", "users"}


def _values(values: Iterable[str | int] | None) -> list[str | int]:
    result = []
    seen = set()
    for value in values or []:
        normalized = value.strip() if isinstance(value, str) else value
        if normalized in (None, "") or normalized in seen:
            continue
        seen.add(normalized)
        result.append(normalized)
    return result


def resolve_admin_recipients(db: Session, target_type: str, target_values=None) -> list[models.User]:
    if target_type not in ADMIN_TARGETS:
        raise ValueError("不支持的发送范围")
    values = _values(target_values)
    if target_type in {"all", "students", "teachers"} and values:
        raise ValueError("该发送范围不应包含额外目标")
    q = db.query(models.User).filter(models.User.role.in_(["student", "teacher"]))
    if target_type == "students":
        q = q.filter(models.User.role == "student")
    elif target_type == "teachers":
        q = q.filter(models.User.role == "teacher")
    elif target_type == "classes":
        if not values:
            raise ValueError("请选择班级")
        requested = {int(v) for v in values}
        existing = {row[0] for row in db.query(models.Class.id).filter(models.Class.id.in_(requested)).all()}
        if requested != existing:
            raise ValueError("发送范围包含不存在的班级")
        q = q.filter(models.User.role == "student", models.User.class_id.in_(requested))
    elif target_type == "majors":
        if not values:
            raise ValueError("请选择专业")
        requested = {int(v) for v in values}
        existing = {row[0] for row in db.query(models.Major.id).filter(models.Major.id.in_(requested)).all()}
        if requested != existing:
            raise ValueError("发送范围包含不存在的专业")
        q = q.filter(models.User.role == "student", models.User.major_id.in_(requested))
    elif target_type == "subjects":
        if not values:
            raise ValueError("请选择体育选科")
        requested = {str(v) for v in values}
        existing = {row[0] for row in db.query(models.User.subject).filter(models.User.role == "student", models.User.subject.in_(requested)).distinct().all()}
        if requested != existing:
            raise ValueError("发送范围包含不存在的体育选科")
        q = q.filter(models.User.role == "student", models.User.subject.in_(requested))
    elif target_type == "users":
        if not values:
            raise ValueError("请选择用户")
        requested = {int(v) for v in values}
        q = q.filter(models.User.id.in_(requested))
        users = q.order_by(models.User.id).all()
        if requested != {row.id for row in users}:
            raise ValueError("发送范围包含不存在或不可接收通知的用户")
        return users
    return q.order_by(models.User.id).all()


async def resolve_teacher_recipients(
    db: Session,
    teacher: models.User,
    target_type: str,
    target_values=None,
) -> list[models.User]:
    if target_type not in TEACHER_TARGETS:
        raise ValueError("不支持的教师发送范围")
    values = _values(target_values)
    q = await get_managed_students_query(teacher, db)
    if target_type == "all_managed" and values:
        raise ValueError("全部管辖学生范围不应包含额外目标")
    if target_type == "classes":
        if not values:
            raise ValueError("请选择班级")
        requested = {int(v) for v in values}
        allowed = {row[0] for row in q.with_entities(models.User.class_id).filter(models.User.class_id.isnot(None)).distinct().all()}
        if not requested.issubset(allowed):
            raise ValueError("发送范围包含非本人管辖班级")
        q = q.filter(models.User.class_id.in_(requested))
    elif target_type == "subjects":
        if not values:
            raise ValueError("请选择体育选科")
        requested = {str(v) for v in values}
        allowed = {row[0] for row in q.with_entities(models.User.subject).filter(models.User.subject.isnot(None)).distinct().all()}
        if not requested.issubset(allowed):
            raise ValueError("发送范围包含非本人管辖选科")
        q = q.filter(models.User.subject.in_(requested))
    elif target_type == "users":
        if not values:
            raise ValueError("请选择学生")
        requested = {int(v) for v in values}
        allowed = {row[0] for row in q.with_entities(models.User.id).all()}
        if not requested.issubset(allowed):
            raise ValueError("发送范围包含非本人管辖学生")
        q = q.filter(models.User.id.in_(requested))
    return q.order_by(models.User.id).all()


def preview_users(users: list[models.User]) -> dict:
    return {
        "recipient_count": len(users),
        "sample_users": [
            {"id": user.id, "name": user.name, "student_id": user.student_id, "role": user.role}
            for user in users[:10]
        ],
    }


def create_campaign(
    db: Session,
    *,
    sender: models.User,
    users: list[models.User],
    title: str,
    body: str,
    ntype: str,
    target_type: str,
    target_values: list[str | int],
    action_type: str | None = None,
    action_data: dict | None = None,
) -> models.NotificationCampaign:
    title, body, ntype, action_type, action_data = validate_notification(
        title, body, ntype, action_type, action_data
    )
    if not users:
        raise ValueError("当前范围内没有可接收通知的用户")
    campaign = models.NotificationCampaign(
        title=title,
        body=body,
        ntype=ntype,
        sender_user_id=sender.id,
        sender_role=sender.role,
        target_type=target_type,
        target_spec=json.dumps(_values(target_values), ensure_ascii=False),
        recipient_count=len(users),
        status="sent",
    )
    db.add(campaign)
    db.flush()
    create_notifications(
        db,
        [user.id for user in users],
        title,
        body,
        ntype,
        action_data,
        campaign_id=campaign.id,
        sender_user_id=sender.id,
        action_type=action_type,
        action_data=action_data,
    )
    return campaign


def campaign_stats(db: Session, campaign: models.NotificationCampaign) -> dict:
    read_count = db.query(models.UserNotification).filter(
        models.UserNotification.campaign_id == campaign.id,
        models.UserNotification.is_read.is_(True),
    ).count()
    total = int(campaign.recipient_count or 0)
    try:
        target_values = json.loads(campaign.target_spec or "[]")
    except (TypeError, ValueError):
        target_values = []
    return {
        "id": campaign.id,
        "title": campaign.title,
        "body": campaign.body,
        "ntype": campaign.ntype,
        "sender_user_id": campaign.sender_user_id,
        "sender_name": campaign.sender.display_name if campaign.sender else "系统",
        "sender_role": campaign.sender_role,
        "target_type": campaign.target_type,
        "target_values": target_values,
        "recipient_count": total,
        "read_count": read_count,
        "unread_count": max(0, total - read_count),
        "read_rate": round(read_count * 100 / total, 1) if total else 0.0,
        "status": campaign.status,
        "created_at": campaign.created_at,
    }
