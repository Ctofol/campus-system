from typing import Optional

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
    ).update({"is_read": True})
    db.commit()
    return {"ok": True}


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
    row.is_read = True
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
    )
    db.commit()
    return {"sent": sent}
