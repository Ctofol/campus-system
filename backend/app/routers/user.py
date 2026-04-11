from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import models, schemas, auth, database

router = APIRouter(prefix="/users", tags=["users"])

get_db = database.get_db

@router.get("/profile", response_model=schemas.UserProfile)
def get_my_profile(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    db.refresh(current_user)
    profile_data = {
        "id": current_user.id,
        "name": current_user.name,
        "phone": current_user.phone,
        "role": current_user.role,
        "student_id": current_user.student_id,
        "group_name": current_user.group_name,
        "health_status": current_user.health_status,
        "signature": getattr(current_user, 'signature', None),
        "avatar_url": getattr(current_user, 'avatar_url', None),
        "class_name": current_user.class_name,
        "class_id": current_user.class_id,
        "major": current_user.major,
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
    
    if profile_update.signature is not None:
        current_user.signature = profile_update.signature
    
    if profile_update.avatar_url is not None:
        current_user.avatar_url = profile_update.avatar_url
    
    db.commit()
    db.refresh(current_user)
    return {"success": True, "message": "Profile updated successfully"}
