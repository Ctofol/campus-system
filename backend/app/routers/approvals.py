from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/approvals", tags=["approvals"])

@router.get("/pending")
async def get_pending_approvals(
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    """Get pending health requests from students in teacher's classes"""
    
    # Get teacher's class IDs
    teacher_classes = db.query(models.Class).filter(
        models.Class.teacher_id == current_user.id
    ).all()
    teacher_class_ids = [c.id for c in teacher_classes]
    
    if not teacher_class_ids:
        return []
    
    # Get pending health requests from students in teacher's classes
    pending_requests = db.query(models.HealthRequest).join(
        models.User, models.HealthRequest.student_id == models.User.id
    ).filter(
        models.HealthRequest.status == "pending",
        models.User.class_id.in_(teacher_class_ids)
    ).order_by(models.HealthRequest.created_at.desc()).all()
    
    result = []
    for req in pending_requests:
        student = db.query(models.User).filter(models.User.id == req.student_id).first()
        result.append({
            "id": req.id,
            "student_name": student.name if student else "Unknown",
            "type": "请假" if req.type == "leave" else "受伤报备",
            "reason": req.reason or "无",
            "created_at": req.created_at.isoformat()
        })
    
    return result

@router.post("/{approval_id}/approve")
async def approve_request(
    approval_id: int,
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    """Approve a health request"""
    
    # Get the health request
    health_request = db.query(models.HealthRequest).filter(
        models.HealthRequest.id == approval_id
    ).first()
    
    if not health_request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # Verify the student is in teacher's class
    student = db.query(models.User).filter(
        models.User.id == health_request.student_id
    ).first()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    teacher_class = db.query(models.Class).filter(
        models.Class.id == student.class_id,
        models.Class.teacher_id == current_user.id
    ).first()
    
    if not teacher_class:
        raise HTTPException(status_code=403, detail="Not authorized to approve this request")
    
    # Update request status
    health_request.status = "approved"
    health_request.updated_at = datetime.utcnow()
    
    # Update student health status
    if health_request.type == "leave":
        student.health_status = "leave"
        student.abnormal_reason = health_request.reason
    elif health_request.type == "injury":
        student.health_status = "injured"
        student.abnormal_reason = health_request.reason
    
    db.commit()
    
    return {"success": True, "message": "Request approved"}

@router.post("/{approval_id}/reject")
async def reject_request(
    approval_id: int,
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    """Reject a health request"""
    
    # Get the health request
    health_request = db.query(models.HealthRequest).filter(
        models.HealthRequest.id == approval_id
    ).first()
    
    if not health_request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # Verify the student is in teacher's class
    student = db.query(models.User).filter(
        models.User.id == health_request.student_id
    ).first()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    teacher_class = db.query(models.Class).filter(
        models.Class.id == student.class_id,
        models.Class.teacher_id == current_user.id
    ).first()
    
    if not teacher_class:
        raise HTTPException(status_code=403, detail="Not authorized to reject this request")
    
    # Update request status
    health_request.status = "rejected"
    health_request.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"success": True, "message": "Request rejected"}
