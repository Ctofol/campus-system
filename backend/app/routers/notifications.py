from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import auth, models, schemas
from ..database import get_db
from ..services.notification_service import (
    create_notifications,
    sanitize_notification_type,
)


router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[schemas.UserNotificationOut])
def list_my_notifications(
    unread_only: bool = Query(False),
    ntype: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    page: int = Query(1, ge=1),
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(models.UserNotification).filter(
        models.UserNotification.user_id == current_user.id
    )
    if unread_only:
        q = q.filter(models.UserNotification.is_read.is_(False))
    if ntype:
        q = q.filter(models.UserNotification.ntype == sanitize_notification_type(ntype))
    return (
        q.order_by(models.UserNotification.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )


@router.get("/unread-count", response_model=schemas.UserNotificationUnread)
def my_notification_unread_count(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    count = (
        db.query(models.UserNotification)
        .filter(
            models.UserNotification.user_id == current_user.id,
            models.UserNotification.is_read.is_(False),
        )
        .count()
    )
    return {"count": count}


@router.put("/read-all")
def mark_all_notifications_read(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    db.query(models.UserNotification).filter(
        models.UserNotification.user_id == current_user.id,
        models.UserNotification.is_read.is_(False),
    ).update({"is_read": True, "read_at": datetime.utcnow()})
    db.commit()
    return {"ok": True}


@router.get("/{notification_id}", response_model=schemas.UserNotificationOut)
def get_my_notification(
    notification_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    row = db.query(models.UserNotification).filter(
        models.UserNotification.id == notification_id,
        models.UserNotification.user_id == current_user.id,
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="通知不存在")
    result = schemas.UserNotificationOut.model_validate(row).model_dump()
    action_data = row.action_data
    target = None
    target_id = None
    if row.action_type == "task_detail":
        target, target_id = models.Task, action_data.get("task_id")
    elif row.action_type == "health_request":
        target, target_id = models.HealthRequest, action_data.get("request_id")
    elif row.action_type == "run_group":
        target, target_id = models.RunGroup, action_data.get("group_id")
    elif row.action_type == "run_group_activity":
        target, target_id = models.RunGroupActivity, action_data.get("activity_id")
    elif row.action_type == "student_detail":
        target, target_id = models.User, action_data.get("student_id")
    elif row.action_type == "score_detail":
        target, target_id = models.Activity, action_data.get("activity_id")
    if target is not None and (not target_id or not db.query(target).filter(target.id == target_id).first()):
        result["action_available"] = False
        result["action_message"] = "关联内容已删除或暂不可用，通知正文仍可正常查看。"
    return result


@router.put("/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    row = (
        db.query(models.UserNotification)
        .filter(
            models.UserNotification.id == notification_id,
            models.UserNotification.user_id == current_user.id,
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="通知不存在")
    if not row.is_read:
        row.is_read = True
        row.read_at = datetime.utcnow()
    db.commit()
    return {"ok": True}


def _student_teacher_ids(student: models.User, db: Session) -> list[int]:
    ids = set()
    if student.class_id:
        cls = db.query(models.Class).filter(models.Class.id == student.class_id).first()
        if cls and cls.teacher_id:
            ids.add(cls.teacher_id)
        if cls:
            for row in (
                db.query(models.TeacherClass.teacher_id)
                .filter(models.TeacherClass.class_name == cls.name)
                .all()
            ):
                ids.add(row.teacher_id)
    if student.subject:
        for row in (
            db.query(models.TeacherSubject.teacher_id)
            .filter(models.TeacherSubject.subject_name == student.subject)
            .all()
        ):
            ids.add(row.teacher_id)
    for row in (
        db.query(models.TeacherStudent.teacher_id)
        .filter(models.TeacherStudent.student_user_id == student.id)
        .all()
    ):
        ids.add(row.teacher_id)
    return list(ids)


@router.post("/to-teachers")
def send_to_my_teachers(
    payload: schemas.NotificationToTeacher,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="仅学生可向老师发送通知")
    teacher_ids = _student_teacher_ids(current_user, db)
    if not teacher_ids:
        raise HTTPException(status_code=404, detail="暂未找到可接收消息的老师")
    sent = create_notifications(
        db,
        teacher_ids,
        payload.title or "学生消息",
        f"{current_user.name}：{payload.message}",
        "student_message",
        {"student_id": current_user.id},
        sender_user_id=current_user.id,
        source_type="student_message",
        source_id=current_user.id,
        action_type="student_detail",
        action_data={"student_id": current_user.id},
    )
    db.commit()
    return {"sent": sent}
