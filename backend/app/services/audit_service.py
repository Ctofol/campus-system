"""关键操作审计服务。"""

import json
from typing import Any

from sqlalchemy.orm import Session

from .. import models


_SENSITIVE_DETAIL_KEYS = frozenset({
    "password",
    "password_hash",
    "token",
    "access_token",
    "refresh_token",
    "embedding",
    "embedding_json",
    "face_embedding",
})


def _safe_detail(value: Any) -> Any:
    """递归移除容易误写入审计日志的认证与人脸特征字段。"""

    if isinstance(value, dict):
        return {
            key: _safe_detail(item)
            for key, item in value.items()
            if str(key).casefold() not in _SENSITIVE_DETAIL_KEYS
        }
    if isinstance(value, list):
        return [_safe_detail(item) for item in value]
    return value


def record_audit(
    db: Session,
    *,
    actor: models.User | None,
    action: str,
    resource_type: str,
    resource_id: int | str | None = None,
    detail: dict[str, Any] | None = None,
) -> None:
    """写入不包含密码、Token、人脸特征等敏感信息的审计记录。"""

    db.add(models.AuditLog(
        actor_user_id=getattr(actor, "id", None),
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id) if resource_id is not None else None,
        detail=json.dumps(_safe_detail(detail), ensure_ascii=False) if detail else None,
    ))
