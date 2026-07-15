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

MAX_TITLE_LENGTH = 60
MAX_BODY_LENGTH = 500
MAX_PAYLOAD_LENGTH = 2000


def sanitize_notification_type(ntype: str | None) -> str:
    value = (ntype or "system").strip()
    return value if value in ALLOWED_NOTIFICATION_TYPES else "system"


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
) -> models.UserNotification:
    clean_title = sanitize_text(title, MAX_TITLE_LENGTH) or "通知"
    clean_body = sanitize_text(body, MAX_BODY_LENGTH)
    note = models.UserNotification(
        user_id=user_id,
        title=clean_title,
        body=clean_body,
        ntype=sanitize_notification_type(ntype),
        payload=sanitize_payload(payload),
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
) -> int:
    count = 0
    seen = set()
    for uid in user_ids:
        if not uid or uid in seen:
            continue
        seen.add(uid)
        create_notification(db, uid, title, body, ntype, payload)
        count += 1
    return count
