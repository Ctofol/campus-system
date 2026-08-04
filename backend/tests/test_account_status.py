import asyncio

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from starlette.requests import Request

from app import auth, config, models, schemas
from app.database import Base
from app.routers import admin as admin_router
from app.routers import auth as auth_router


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def _request():
    return Request({"type": "http", "client": ("127.0.0.1", 12345), "headers": []})


def _user(db, role, name, password="Password2026", **kwargs):
    row = models.User(
        role=role,
        name=name,
        password_hash=auth.get_password_hash(password),
        **kwargs,
    )
    db.add(row)
    db.commit()
    return row


def test_disabled_account_loses_existing_token_and_cannot_login(db):
    admin = _user(db, "admin", "管理员")
    student = _user(db, "student", "学生", student_id="S2026001")
    token = auth.create_user_access_token(student)

    result = admin_router.disable_user(
        student.id,
        schemas.DisableAccountRequest(reason="离校"),
        db,
        admin,
    )
    assert result["is_active"] is False
    with pytest.raises(HTTPException) as token_error:
        asyncio.run(auth.get_current_user_allow_incomplete(token=token, db=db))
    assert token_error.value.status_code == 401

    with pytest.raises(HTTPException, match="账号已停用") as login_error:
        auth_router.login(
            schemas.UserLogin(account="S2026001", password="Password2026"),
            _request(),
            db,
        )
    assert login_error.value.status_code == 403


def test_account_can_login_again_after_enable(db):
    admin = _user(db, "admin", "管理员")
    student = _user(db, "student", "学生", student_id="S2026002")
    admin_router.disable_user(student.id, schemas.DisableAccountRequest(), db, admin)
    admin_router.enable_user(student.id, db, admin)

    response = auth_router.login(
        schemas.UserLogin(account="S2026002", password="Password2026"),
        _request(),
        db,
    )
    assert response["user_id"] == student.id


def test_admin_cannot_be_disabled(db):
    admin = _user(db, "admin", "管理员")
    with pytest.raises(HTTPException, match="管理员账号不能停用"):
        admin_router.disable_user(admin.id, schemas.DisableAccountRequest(), db, admin)


def test_teacher_staff_id_is_stored_and_can_be_used_to_login(db):
    admin = _user(db, "admin", "管理员")
    teacher = admin_router.create_user(
        schemas.UserCreate(name="教师", role="teacher", staff_id="T2026001"),
        db=db,
        current_user=admin,
    )
    assert teacher.staff_id == "T2026001"
    assert teacher.student_id is None

    response = auth_router.login(
        schemas.UserLogin(account="T2026001", password=config.INITIAL_ACCOUNT_PASSWORD),
        _request(),
        db,
    )
    assert response["staff_id"] == "T2026001"
