from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, auth, database

router = APIRouter(prefix="/users", tags=["users"])

get_db = database.get_db


def _safe_rel_str(getter):
    """班级/专业等关系可能因脏 FK 在懒加载时抛错，避免整接口 500。"""
    try:
        return getter()
    except Exception:
        return None


@router.get("/profile", response_model=schemas.UserProfile)
def get_my_profile(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
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
        "class_name": _safe_rel_str(lambda: current_user.class_name),
        "class_id": current_user.class_id,
        "major": _safe_rel_str(lambda: current_user.major),
        "major_id": current_user.major_id,
        "subject": current_user.subject,
    }
    return profile_data

@router.put("/profile")
def update_my_profile(
    profile_update: schemas.UserProfileUpdate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    if profile_update.name:
        current_user.name = profile_update.name

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
    
    if profile_update.signature is not None:
        current_user.signature = profile_update.signature
    
    if profile_update.avatar_url is not None:
        current_user.avatar_url = profile_update.avatar_url
    
    db.commit()
    db.refresh(current_user)
    return {"success": True, "message": "Profile updated successfully"}
