import asyncio
import io

import pandas as pd
import pytest
from fastapi import HTTPException, Request, UploadFile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import auth, models, schemas
from app.routers import auth as auth_router
from app.routers import user as user_router
from app.routers import admin as admin_router


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


def _pending_student(db, *, student_id="20260001", name="张三"):
    major = models.Major(name="信息安全")
    db.add(major)
    db.flush()
    target_class = models.Class(name="一班", major_id=major.id)
    profile = models.StudentProfile(
        student_id=student_id,
        full_name=name,
        gender="male",
        class_name="一班",
        major="信息安全",
        is_activated=True,
    )
    db.add_all([target_class, profile])
    db.flush()
    user = models.User(
        role="student",
        name=name,
        phone=None,
        password_hash=auth.get_password_hash("123456"),
        must_change_password=True,
        token_version=0,
        student_id=student_id,
        class_id=target_class.id,
        major_id=major.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _request():
    return Request({"type": "http", "client": ("127.0.0.1", 12345), "headers": []})


def test_public_registration_is_closed():
    with pytest.raises(HTTPException) as exc_info:
        auth_router.register()
    assert exc_info.value.status_code == 403


def test_pending_account_is_limited_until_completion(db):
    user = _pending_student(db)
    response = auth_router.login(
        schemas.UserLogin(account=user.student_id, password="123456"),
        _request(),
        db,
    )
    assert response["must_complete_account"] is True
    assert response["phone"] is None

    resolved = asyncio.run(
        auth.get_current_user_allow_incomplete(response["access_token"], db)
    )
    assert resolved.id == user.id
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(auth.get_current_user(resolved))
    assert exc_info.value.status_code == 403

    with pytest.raises(HTTPException, match="姓名"):
        auth_router.complete_account(
            schemas.CompleteAccountRequest(
                real_name="李四",
                phone="13800138000",
                new_password="Student2026",
            ),
            db,
            user,
        )

    completed = auth_router.complete_account(
        schemas.CompleteAccountRequest(
            real_name="张三",
            phone="13800138000",
            new_password="Student2026",
            nickname="小张",
        ),
        db,
        user,
    )
    assert completed["must_complete_account"] is False
    assert completed["nickname"] == "小张"
    assert completed["display_name"] == "小张"
    assert auth.verify_password("Student2026", user.password_hash)

    with pytest.raises(HTTPException) as exc_info:
        auth_router.login(
            schemas.UserLogin(account=user.student_id, password="123456"),
            _request(),
            db,
        )
    assert exc_info.value.status_code == 401


def test_password_and_phone_changes_require_current_password(db):
    user = _pending_student(db)
    auth_router.complete_account(
        schemas.CompleteAccountRequest(
            real_name=user.name,
            phone="13800138000",
            new_password="Student2026",
        ),
        db,
        user,
    )
    token_before = auth.create_user_access_token(user)

    with pytest.raises(HTTPException, match="当前密码"):
        user_router.change_phone(
            schemas.ChangePhoneRequest(
                current_password="wrong-password",
                new_phone="13900139000",
            ),
            user,
            db,
        )
    changed = user_router.change_phone(
        schemas.ChangePhoneRequest(
            current_password="Student2026",
            new_phone="13900139000",
        ),
        user,
        db,
    )
    assert changed["phone"] == "13900139000"
    assert asyncio.run(auth.get_current_user_allow_incomplete(token_before, db)).id == user.id

    result = user_router.change_password(
        schemas.ChangePasswordRequest(
            old_password="Student2026",
            new_password="Student2027",
        ),
        user,
        db,
    )
    assert result["success"] is True
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(auth.get_current_user_allow_incomplete(token_before, db))
    assert exc_info.value.status_code == 401


def test_real_name_and_phone_cannot_be_changed_through_profile(db):
    user = _pending_student(db)
    user.must_change_password = False
    user.phone = "13800138000"
    db.commit()

    with pytest.raises(HTTPException, match="真实姓名"):
        user_router.update_my_profile(
            schemas.UserProfileUpdate(name="新姓名"), user, db
        )
    with pytest.raises(HTTPException, match="账号安全"):
        user_router.update_my_profile(
            schemas.UserProfileUpdate(phone="13900139000"), user, db
        )

    result = user_router.update_my_profile(
        schemas.UserProfileUpdate(nickname="昵称"), user, db
    )
    assert result["success"] is True
    assert user.nickname == "昵称"


def test_admin_student_import_creates_pending_account_without_phone(db):
    admin = models.User(
        role="admin",
        name="管理员",
        phone="13700137000",
        password_hash=auth.get_password_hash("Admin2026"),
        must_change_password=False,
    )
    db.add(admin)
    db.commit()

    frame = pd.DataFrame(
        [
            {
                "学号": "20260009",
                "姓名": "王同学",
                "性别": "女",
                "所属班级名称": "二班",
                "专业/课程": "治安管理",
                "选科": "篮球",
            }
        ]
    )
    payload = io.BytesIO()
    frame.to_excel(payload, index=False)
    payload.seek(0)
    result = asyncio.run(
        admin_router.import_students(
            UploadFile(filename="students.xlsx", file=payload),
            db,
            admin,
        )
    )
    assert result["success"] == 1
    student = db.query(models.User).filter_by(student_id="20260009").one()
    assert student.phone is None
    assert student.must_change_password is True
    assert student.gender == "female"
    assert student.subject == "篮球"
    assert auth.verify_password("123456", student.password_hash)

    admin_router.reset_password(student.id, db, admin)
    assert student.must_change_password is True
    assert student.token_version == 1


def test_admin_can_create_one_pending_account_and_account_id_is_unique(db):
    admin = models.User(
        role="admin",
        name="管理员",
        phone="13700137001",
        password_hash=auth.get_password_hash("Admin2026"),
        must_change_password=False,
    )
    db.add(admin)
    db.commit()

    created = admin_router.create_user(
        schemas.UserCreate(
            name="李同学",
            role="student",
            student_id="20260010",
        ),
        db=db,
        current_user=admin,
    )
    assert created.student_id == "20260010"
    assert created.phone is None
    assert created.must_change_password is True
    assert auth.verify_password("123456", created.password_hash)
    assert db.query(models.AuditLog).filter_by(
        action="user.create", resource_id=str(created.id)
    ).one()

    with pytest.raises(HTTPException, match="学号或工号已存在"):
        admin_router.create_user(
            schemas.UserCreate(
                name="重复账号",
                role="student",
                student_id="20260010",
            ),
            db=db,
            current_user=admin,
        )
