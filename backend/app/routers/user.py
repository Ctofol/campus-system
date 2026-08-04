import re

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, auth, database, config
from ..db_migrate import ensure_schema_upgrades
from ..services.face_profile_service import profile_to_status, upsert_student_face_profile
from ..services.audit_service import record_audit

router = APIRouter(prefix="/users", tags=["users"])

get_db = database.get_db


def _safe_rel_str(getter):
    """班级/专业等关系可能因脏 FK 在懒加载时抛错，避免整接口 500。"""
    try:
        return getter()
    except Exception:
        return None


@router.get("/face-profile", response_model=schemas.FaceProfileStatusOut)
def get_my_face_profile(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    ensure_schema_upgrades()
    db.refresh(current_user)
    return profile_to_status(getattr(current_user, "face_profile", None))


@router.post("/face-profile", response_model=schemas.FaceProfileStatusOut)
def submit_my_face_profile(
    payload: schemas.FaceProfileSubmit,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    ensure_schema_upgrades()
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="仅学生可以提交人脸认证资料")
    image_url = (payload.image_url or "").strip()
    if not image_url:
        raise HTTPException(status_code=400, detail="请先上传用于认证的人脸照片")
    try:
        profile = upsert_student_face_profile(db, current_user, image_url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return profile_to_status(profile)


@router.get("/profile", response_model=schemas.UserProfile)
def get_my_profile(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    ensure_schema_upgrades()
    # 与 get_current_user 共用同一请求的 get_db 时 refresh 安全；若仅读列也可省略
    db.refresh(current_user)
    # 旧库可能为 NULL；UserProfile 中 name/phone/role/health_status 为必填 str，缺省会触发响应校验 → 500
    health = current_user.health_status or "normal"
    profile_data = {
        "id": current_user.id,
        "name": (current_user.name or "").strip() or "未命名",
        "phone": current_user.phone or "",
        "role": current_user.role or "student",
        "nickname": current_user.nickname,
        "display_name": current_user.display_name,
        "must_complete_account": bool(current_user.must_change_password),
        "student_id": current_user.student_id,
        "group_name": current_user.group_name,
        "health_status": health,
        "signature": getattr(current_user, 'signature', None),
        "avatar_url": getattr(current_user, 'avatar_url', None),
        "header_bg_url": getattr(current_user, 'header_bg_url', None),
        "class_name": _safe_rel_str(lambda: current_user.class_name),
        "class_id": current_user.class_id,
        "major": _safe_rel_str(lambda: current_user.major),
        "major_id": current_user.major_id,
        "subject": current_user.subject,
        "weekly_run_goal_km": float(current_user.weekly_run_goal_km or 0)
        if getattr(current_user, "weekly_run_goal_km", None)
        else 0.0,
        "face_profile_status": profile_to_status(getattr(current_user, "face_profile", None)).get("status"),
        "face_profile_updated_at": profile_to_status(getattr(current_user, "face_profile", None)).get("updated_at"),
    }
    return profile_data

@router.put("/profile")
def update_my_profile(
    profile_update: schemas.UserProfileUpdate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    ensure_schema_upgrades()
    if profile_update.name is not None and (
        str(profile_update.name).strip() != (current_user.name or "").strip()
    ):
        raise HTTPException(status_code=403, detail="真实姓名以学校档案为准，请联系管理员修改")
    if profile_update.phone is not None and (
        str(profile_update.phone).strip() != (current_user.phone or "").strip()
    ):
        raise HTTPException(status_code=400, detail="请在账号安全中验证密码后修改手机号")
    if profile_update.nickname is not None:
        current_user.nickname = str(profile_update.nickname).strip()[:32] or None
    
    if profile_update.signature is not None:
        current_user.signature = str(profile_update.signature).strip()[:100]
    
    if profile_update.avatar_url is not None:
        current_user.avatar_url = str(profile_update.avatar_url).strip()[:512]

    if profile_update.header_bg_url is not None:
        current_user.header_bg_url = str(profile_update.header_bg_url).strip()[:512]

    if profile_update.weekly_run_goal_km is not None:
        km = float(profile_update.weekly_run_goal_km)
        current_user.weekly_run_goal_km = None if km <= 0 else round(min(999.0, km), 1)

    db.commit()
    db.refresh(current_user)
    return {"success": True, "message": "个人资料已更新"}


@router.post("/change-password")
def change_password(
    payload: schemas.ChangePasswordRequest,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    if not auth.verify_password(payload.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="原密码不正确")
    try:
        new_password = auth.validate_new_password(payload.new_password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if auth.verify_password(new_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="新密码不能与原密码相同")

    current_user.password_hash = auth.get_password_hash(new_password)
    current_user.token_version = int(current_user.token_version or 0) + 1
    record_audit(
        db,
        actor=current_user,
        action="user.change_password",
        resource_type="user",
        resource_id=current_user.id,
    )
    db.commit()
    return {"success": True, "message": "密码已修改，请重新登录"}


@router.post("/change-phone")
def change_phone(
    payload: schemas.ChangePhoneRequest,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    if not auth.verify_password(payload.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="当前密码不正确")
    phone = (payload.new_phone or "").strip()
    if not re.fullmatch(r"1[3-9]\d{9}", phone):
        raise HTTPException(status_code=400, detail="请输入正确的手机号")
    duplicate = db.query(models.User).filter(
        models.User.phone == phone,
        models.User.id != current_user.id,
    ).first()
    if duplicate:
        raise HTTPException(status_code=400, detail="该手机号已被绑定")
    old_phone = current_user.phone
    current_user.phone = phone
    record_audit(
        db,
        actor=current_user,
        action="user.change_phone",
        resource_type="user",
        resource_id=current_user.id,
        detail={"had_phone": bool(old_phone)},
    )
    db.commit()
    return {"success": True, "message": "手机号已更新", "phone": phone}
