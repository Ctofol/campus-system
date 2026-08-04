import asyncio
import json

import pytest
from fastapi import HTTPException

from app.routers.admin import get_current_admin
from app.services.audit_service import record_audit


class _User:
    def __init__(self, user_id: int, role: str):
        self.id = user_id
        self.role = role


class _Session:
    def __init__(self):
        self.rows = []

    def add(self, row):
        self.rows.append(row)


def test_admin_dependency_rejects_non_admin_user():
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(get_current_admin(_User(2, "student")))

    assert exc_info.value.status_code == 403


def test_admin_dependency_accepts_admin_user():
    admin = _User(1, "admin")
    assert asyncio.run(get_current_admin(admin)) is admin


def test_audit_record_masks_sensitive_detail_fields():
    session = _Session()

    record_audit(
        session,
        actor=_User(1, "admin"),
        action="user.reset_password",
        resource_type="user",
        resource_id=2,
        detail={
            "role": "student",
            "password": "should-not-be-stored",
            "nested": {"access_token": "should-not-be-stored", "reason": "manual"},
        },
    )

    assert len(session.rows) == 1
    row = session.rows[0]
    assert row.actor_user_id == 1
    assert row.resource_id == "2"
    assert json.loads(row.detail) == {"role": "student", "nested": {"reason": "manual"}}
