import json
import re
from typing import Iterable

from sqlalchemy.orm import Session

from .. import models


ALLOWED_NOTIFICATION_TYPES = {
    "system",
    "update",
    "task",
    "task_reminder",
    "teacher_message",
    "student_message",
    "health_review",
    "run_group",
    "run_group_activity",
    "run_group_apply",
    "interaction",
    "score",
}

ALLOWED_ACTION_TYPES = {
    "task_detail",
    "health_request",
    "run_group",
    "run_group_activity",
    "score_detail",
    "student_detail",
}

MAX_TITLE_LENGTH = 60
MAX_BODY_LENGTH = 500
MAX_PAYLOAD_LENGTH = 2000


def sanitize_notification_type(ntype: str | None) -> str:
    value = (ntype or "system").strip()
    return value if value in ALLOWED_NOTIFICATION_TYPES else "system"


def validate_notification(
    title: str,
    body: str = "",
    ntype: str = "system",
    action_type: str | None = None,
    action_data: dict | None = None,
) -> tuple[str, str, str, str | None, dict]:
    clean_title = sanitize_text(title, MAX_TITLE_LENGTH)
    clean_body = sanitize_text(body, MAX_BODY_LENGTH)
    if not clean_title:
        raise ValueError("通知标题不能为空")
    if len(str(title or "").strip()) > MAX_TITLE_LENGTH:
        raise ValueError(f"通知标题不能超过{MAX_TITLE_LENGTH}个字符")
    if len(str(body or "").strip()) > MAX_BODY_LENGTH:
        raise ValueError(f"通知内容不能超过{MAX_BODY_LENGTH}个字符")
    clean_type = (ntype or "system").strip()
    if clean_type not in ALLOWED_NOTIFICATION_TYPES:
        raise ValueError("不支持的通知类型")
    if action_type and action_type not in ALLOWED_ACTION_TYPES:
        raise ValueError("不支持的通知跳转类型")
    raw_action = sanitize_payload(action_data)
    safe_action = json.loads(raw_action) if raw_action else {}
    return clean_title, clean_body, clean_type, action_type, safe_action


def sanitize_text(value: str | None, max_len: int) -> str:
    text = "" if value is None else str(value)
    text = re.sub(r"<[^>]*>", "", text)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > max_len:
        text = text[: max_len - 1].rstrip() + "…"
    return text


def sanitize_payload(payload: dict | None) -> str | None:
    if not payload:
        return None
    safe = {}
    for key, value in payload.items():
        k = sanitize_text(str(key), 50)
        if not k:
            continue
        if isinstance(value, (str, int, float, bool)) or value is None:
            safe[k] = value
        else:
            safe[k] = sanitize_text(str(value), 200)
    raw = json.dumps(safe, ensure_ascii=False)
    if len(raw) > MAX_PAYLOAD_LENGTH:
        return None
    return raw


def create_notification(
    db: Session,
    user_id: int,
    title: str,
    body: str = "",
    ntype: str = "system",
    payload: dict | None = None,
    *,
    campaign_id: int | None = None,
    sender_user_id: int | None = None,
    source_type: str | None = None,
    source_id: int | str | None = None,
    action_type: str | None = None,
    action_data: dict | None = None,
    event_key: str | None = None,
) -> models.UserNotification | None:
    clean_title, clean_body, clean_type, action_type, safe_action = validate_notification(
        title, body, ntype, action_type, action_data or payload
    )
    if event_key:
        existing = db.query(models.UserNotification).filter(
            models.UserNotification.user_id == user_id,
            models.UserNotification.event_key == event_key,
        ).first()
        if existing:
            return None
    note = models.UserNotification(
        user_id=user_id,
        title=clean_title,
        body=clean_body,
        ntype=clean_type,
        payload=sanitize_payload(payload),
        campaign_id=campaign_id,
        sender_user_id=sender_user_id,
        source_type=sanitize_text(source_type, 32) or None,
        source_id=sanitize_text(str(source_id), 64) if source_id is not None else None,
        action_type=action_type,
        action_payload=sanitize_payload(safe_action),
        event_key=sanitize_text(event_key, 160) if event_key else None,
    )
    db.add(note)
    return note


def create_notifications(
    db: Session,
    user_ids: Iterable[int],
    title: str,
    body: str = "",
    ntype: str = "system",
    payload: dict | None = None,
    *,
    campaign_id: int | None = None,
    sender_user_id: int | None = None,
    source_type: str | None = None,
    source_id: int | str | None = None,
    action_type: str | None = None,
    action_data: dict | None = None,
    event_key_factory=None,
) -> int:
    count = 0
    seen = set()
    for uid in user_ids:
        if not uid or uid in seen:
            continue
        seen.add(uid)
        event_key = event_key_factory(uid) if event_key_factory else None
        created = create_notification(
            db,
            uid,
            title,
            body,
            ntype,
            payload,
            campaign_id=campaign_id,
            sender_user_id=sender_user_id,
            source_type=source_type,
            source_id=source_id,
            action_type=action_type,
            action_data=action_data,
            event_key=event_key,
        )
        if created is not None:
            count += 1
    return count
