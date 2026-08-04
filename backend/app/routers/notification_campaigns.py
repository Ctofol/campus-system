"""管理员与教师的站内通知批次接口。"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from .. import auth, models, schemas
from ..database import get_db
from ..services.audit_service import record_audit
from ..services.notification_campaign_service import (
    campaign_stats,
    create_campaign,
    preview_users,
    resolve_admin_recipients,
    resolve_teacher_recipients,
)
from ..services.teacher_service import get_managed_students_query


manage_router = APIRouter(prefix="/manage", tags=["notification-campaigns"])
teacher_router = APIRouter(prefix="/teacher", tags=["teacher-notification-campaigns"])


async def _admin_user(current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可执行此操作")
    return current_user


def _bad_request(exc: ValueError):
    raise HTTPException(status_code=400, detail=str(exc)) from exc


@manage_router.get("/notification-targets/options")
def admin_notification_target_options(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(_admin_user),
):
    classes = db.query(models.Class).order_by(models.Class.name).all()
    majors = db.query(models.Major).order_by(models.Major.name).all()
    subjects = [
        row[0] for row in db.query(models.User.subject)
        .filter(models.User.role == "student", models.User.subject.isnot(None), models.User.subject != "")
        .distinct().order_by(models.User.subject).all()
    ]
    return {
        "classes": [{"id": row.id, "name": row.name, "major": row.major_name} for row in classes],
        "majors": [{"id": row.id, "name": row.name} for row in majors],
        "subjects": subjects,
    }


@manage_router.get("/notification-targets/users")
def search_notification_users(
    q: str = Query(..., min_length=2, max_length=40),
    limit: int = Query(30, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(_admin_user),
):
    keyword = f"%{q.strip()}%"
    rows = db.query(models.User).filter(
        models.User.role.in_(["student", "teacher"]),
        or_(
            models.User.name.ilike(keyword),
            models.User.student_id.ilike(keyword),
            models.User.phone.ilike(keyword),
        ),
    ).order_by(models.User.name).limit(limit).all()
    return [
        {
            "id": row.id,
            "name": row.name,
            "student_id": row.student_id,
            "phone": row.phone,
            "role": row.role,
            "class_name": row.plain_class_name,
        }
        for row in rows
    ]


@manage_router.post("/notification-campaigns/preview", response_model=schemas.NotificationCampaignPreview)
def preview_admin_campaign(
    body: schemas.NotificationCampaignRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(_admin_user),
):
    try:
        return preview_users(resolve_admin_recipients(db, body.target_type, body.target_values))
    except (TypeError, ValueError) as exc:
        _bad_request(ValueError(str(exc)))


@manage_router.post("/notification-campaigns", response_model=schemas.NotificationCampaignOut)
def send_admin_campaign(
    body: schemas.NotificationCampaignRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(_admin_user),
):
    try:
        users = resolve_admin_recipients(db, body.target_type, body.target_values)
        campaign = create_campaign(
            db,
            sender=current_user,
            users=users,
            title=body.title,
            body=body.content,
            ntype=body.ntype,
            target_type=body.target_type,
            target_values=body.target_values,
            action_type=body.action_type,
            action_data=body.action_data,
        )
        record_audit(
            db,
            actor=current_user,
            action="notification.campaign.send",
            resource_type="notification_campaign",
            resource_id=campaign.id,
            detail={"target_type": body.target_type, "recipient_count": len(users)},
        )
        db.commit()
        db.refresh(campaign)
        return campaign_stats(db, campaign)
    except (TypeError, ValueError) as exc:
        db.rollback()
        _bad_request(ValueError(str(exc)))


@manage_router.get("/notification-campaigns", response_model=schemas.NotificationCampaignList)
def list_admin_campaigns(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    title: str | None = Query(None, max_length=60),
    ntype: str | None = None,
    target_type: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(_admin_user),
):
    q = db.query(models.NotificationCampaign).options(joinedload(models.NotificationCampaign.sender))
    if title:
        q = q.filter(models.NotificationCampaign.title.ilike(f"%{title.strip()}%"))
    if ntype:
        q = q.filter(models.NotificationCampaign.ntype == ntype)
    if target_type:
        q = q.filter(models.NotificationCampaign.target_type == target_type)
    if date_from:
        q = q.filter(models.NotificationCampaign.created_at >= date_from)
    if date_to:
        q = q.filter(models.NotificationCampaign.created_at <= date_to)
    total = q.count()
    rows = q.order_by(models.NotificationCampaign.created_at.desc()).offset((page - 1) * size).limit(size).all()
    return {"items": [campaign_stats(db, row) for row in rows], "total": total, "page": page, "size": size}


@manage_router.get("/notification-campaigns/{campaign_id}", response_model=schemas.NotificationCampaignOut)
def get_admin_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(_admin_user),
):
    row = db.query(models.NotificationCampaign).options(joinedload(models.NotificationCampaign.sender)).filter_by(id=campaign_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="通知批次不存在")
    return campaign_stats(db, row)


@manage_router.get("/notification-campaigns/{campaign_id}/recipients", response_model=schemas.NotificationRecipientList)
def get_campaign_recipients(
    campaign_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    read_status: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(_admin_user),
):
    if not db.query(models.NotificationCampaign.id).filter_by(id=campaign_id).first():
        raise HTTPException(status_code=404, detail="通知批次不存在")
    q = db.query(models.UserNotification).options(joinedload(models.UserNotification.user)).filter(
        models.UserNotification.campaign_id == campaign_id
    )
    if read_status == "read":
        q = q.filter(models.UserNotification.is_read.is_(True))
    elif read_status == "unread":
        q = q.filter(models.UserNotification.is_read.is_(False))
    elif read_status not in (None, ""):
        raise HTTPException(status_code=400, detail="阅读状态筛选值不正确")
    total = q.count()
    rows = q.order_by(models.UserNotification.id).offset((page - 1) * size).limit(size).all()
    return {
        "items": [
            {
                "notification_id": row.id,
                "user_id": row.user_id,
                "name": row.user.name,
                "student_id": row.user.student_id,
                "phone": row.user.phone,
                "role": row.user.role,
                "is_read": row.is_read,
                "read_at": row.read_at,
            }
            for row in rows
        ],
        "total": total,
        "page": page,
        "size": size,
    }


@teacher_router.get("/notification-targets")
async def teacher_notification_targets(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_teacher),
):
    students = (await get_managed_students_query(current_user, db)).order_by(models.User.name).all()
    class_ids = sorted({row.class_id for row in students if row.class_id})
    classes = db.query(models.Class).filter(models.Class.id.in_(class_ids)).order_by(models.Class.name).all() if class_ids else []
    return {
        "recipient_count": len(students),
        "classes": [{"id": row.id, "name": row.name, "major": row.major_name} for row in classes],
        "subjects": sorted({row.subject for row in students if row.subject}),
        "students": [
            {"id": row.id, "name": row.name, "student_id": row.student_id, "class_name": row.plain_class_name}
            for row in students
        ],
    }


@teacher_router.post("/notification-campaigns/preview", response_model=schemas.NotificationCampaignPreview)
async def preview_teacher_campaign(
    body: schemas.NotificationCampaignRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_teacher),
):
    try:
        return preview_users(await resolve_teacher_recipients(db, current_user, body.target_type, body.target_values))
    except (TypeError, ValueError) as exc:
        _bad_request(ValueError(str(exc)))


@teacher_router.post("/notification-campaigns", response_model=schemas.NotificationCampaignOut)
async def send_teacher_campaign(
    body: schemas.NotificationCampaignRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_teacher),
):
    if body.ntype not in {"teacher_message", "task"}:
        raise HTTPException(status_code=400, detail="教师只能发送教师通知或任务通知")
    try:
        users = await resolve_teacher_recipients(db, current_user, body.target_type, body.target_values)
        campaign = create_campaign(
            db,
            sender=current_user,
            users=users,
            title=body.title,
            body=body.content,
            ntype=body.ntype,
            target_type=body.target_type,
            target_values=body.target_values,
            action_type=body.action_type,
            action_data=body.action_data,
        )
        record_audit(
            db,
            actor=current_user,
            action="notification.campaign.send",
            resource_type="notification_campaign",
            resource_id=campaign.id,
            detail={"target_type": body.target_type, "recipient_count": len(users)},
        )
        db.commit()
        db.refresh(campaign)
        return campaign_stats(db, campaign)
    except (TypeError, ValueError) as exc:
        db.rollback()
        _bad_request(ValueError(str(exc)))
