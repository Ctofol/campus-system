from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, auth, database, config
from ..db_migrate import ensure_schema_upgrades
from ..services.face_profile_service import profile_to_status, upsert_student_face_profile
from datetime import timedelta

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
        raise HTTPException(status_code=403, detail="Only students can submit face profiles")
    image_url = (payload.image_url or "").strip()
    if not image_url:
        raise HTTPException(status_code=400, detail="image_url is required")
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
    if profile_update.name:
        current_user.name = str(profile_update.name).strip()[:50]

    phone_changed = False
    if profile_update.phone is not None:
        phone = str(profile_update.phone).strip()
        if not phone:
            raise HTTPException(status_code=400, detail="手机号不能为空")
        if phone != (current_user.phone or ""):
            exists = db.query(models.User).filter(
                models.User.phone == phone,
                models.User.id != current_user.id
            ).first()
            if exists:
                raise HTTPException(status_code=400, detail="该手机号已被绑定")
            current_user.phone = phone
            phone_changed = True
    
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
    result = {"success": True, "message": "Profile updated successfully"}
    if phone_changed:
        result["access_token"] = auth.create_access_token(
            data={"sub": current_user.phone, "role": current_user.role},
            expires_delta=timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        result["token_type"] = "bearer"
    return result
