from datetime import timedelta
import re

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from .. import models, schemas, auth, database, config
from ..services import login_guard
from ..services.audit_service import record_audit

router = APIRouter(prefix="/auth", tags=["auth"])

get_db = database.get_db

def _token_response(user: models.User, *, setup: bool = False) -> dict:
    access_token = auth.create_user_access_token(
        user,
        scope="account_setup" if setup else "access",
        expires_delta=timedelta(minutes=15) if setup else None,
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "user_id": user.id,
        "name": user.name,
        "nickname": user.nickname,
        "display_name": user.display_name,
        "phone": user.phone,
        "must_complete_account": bool(user.must_change_password),
        "class_name": user.class_name,
        "class_id": user.class_id,
        "student_id": user.student_id,
        "staff_id": user.staff_id,
        "major": user.major,
        "major_id": user.major_id,
        "subject": user.subject,
    }


@router.post("/register")
def register():
    raise HTTPException(status_code=403, detail="学校账号不支持自助注册，请联系管理员")

@router.post("/login", response_model=schemas.Token)
def login(user_data: schemas.UserLogin, request: Request, db: Session = Depends(get_db)):
    account = (user_data.account or user_data.phone or "").strip()
    if not account:
        raise HTTPException(status_code=400, detail="请输入手机号、学号或工号")
    client_host = request.client.host if request.client else "unknown"
    wait_seconds = login_guard.remaining_lock_seconds(account, client_host)
    if wait_seconds:
        raise HTTPException(status_code=429, detail=f"登录失败次数过多，请在 {wait_seconds} 秒后重试")

    user = db.query(models.User).filter(models.User.phone == account).first()
    if not user:
        user = db.query(models.User).filter(models.User.student_id == account).first()
    if not user:
        user = db.query(models.User).filter(models.User.staff_id == account).first()
    if not user or not auth.verify_password(user_data.password, user.password_hash):
        login_guard.record_failure(account, client_host)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账号或密码错误，请确认后重试",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not bool(user.is_active):
        login_guard.clear_failures(account, client_host)
        raise HTTPException(status_code=403, detail="账号已停用，请联系管理员")

    login_guard.clear_failures(account, client_host)
    
    return _token_response(user, setup=bool(user.must_change_password))


@router.post("/complete-account", response_model=schemas.Token)
def complete_account(
    payload: schemas.CompleteAccountRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user_allow_incomplete),
):
    if not current_user.must_change_password:
        raise HTTPException(status_code=409, detail="账号已完成首次设置")
    if (payload.real_name or "").strip() != (current_user.name or "").strip():
        raise HTTPException(status_code=403, detail="姓名与学校档案不符")

    phone = (payload.phone or "").strip()
    if not re.fullmatch(r"1[3-9]\d{9}", phone):
        raise HTTPException(status_code=400, detail="请输入正确的手机号")
    duplicate = db.query(models.User).filter(
        models.User.phone == phone,
        models.User.id != current_user.id,
    ).first()
    if duplicate:
        raise HTTPException(status_code=400, detail="该手机号已被绑定")

    try:
        new_password = auth.validate_new_password(payload.new_password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if auth.verify_password(new_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="新密码不能与初始密码相同")

    current_user.phone = phone
    current_user.nickname = (payload.nickname or "").strip()[:32] or None
    current_user.password_hash = auth.get_password_hash(new_password)
    current_user.must_change_password = False
    current_user.token_version = int(current_user.token_version or 0) + 1
    record_audit(
        db,
        actor=current_user,
        action="account.complete",
        resource_type="user",
        resource_id=current_user.id,
    )
    db.commit()
    db.refresh(current_user)
    return _token_response(current_user)

@router.post("/refresh")
def refresh_token(current_user: models.User = Depends(auth.get_current_user)):
    access_token = auth.create_user_access_token(current_user)
    return {"access_token": access_token, "token_type": "bearer"}
