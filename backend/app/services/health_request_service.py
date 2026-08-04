"""健康报备的状态流转与学生健康状态同步。"""

from datetime import datetime

from sqlalchemy.orm import Session

from .. import models


def _is_active(request: models.HealthRequest, now: datetime) -> bool:
    if request.status != "approved":
        return False
    if request.type == "injury":
        return True
    if request.type in {"leave", "sick"}:
        return bool(
            request.start_date
            and request.end_date
            and request.start_date <= now <= request.end_date
        )
    return True


def recompute_student_health(db: Session, student_id: int, now: datetime | None = None) -> None:
    """按仍生效的已批准报备重算学生状态，伤病优先于请假。"""
    now = now or datetime.utcnow()
    student = db.query(models.User).filter(models.User.id == student_id).first()
    if not student:
        return
    approved = (
        db.query(models.HealthRequest)
        .filter(
            models.HealthRequest.student_id == student_id,
            models.HealthRequest.status == "approved",
        )
        .order_by(models.HealthRequest.reviewed_at.desc(), models.HealthRequest.id.desc())
        .all()
    )
    active = [row for row in approved if _is_active(row, now)]
    injury = next((row for row in active if row.type == "injury"), None)
    leave = next((row for row in active if row.type in {"leave", "sick"}), None)
    selected = injury or leave or (active[0] if active else None)
    if not selected:
        student.health_status = "normal"
        student.abnormal_reason = None
    elif selected.type == "injury":
        student.health_status = "injured"
        student.abnormal_reason = selected.reason
    elif selected.type in {"leave", "sick"}:
        student.health_status = "leave"
        student.abnormal_reason = selected.reason
    else:
        student.health_status = "abnormal"
        student.abnormal_reason = selected.reason


def refresh_expired_health_requests(
    db: Session, student_id: int | None = None, now: datetime | None = None
) -> int:
    """把已过结束时间的请假转为已结束，并恢复或重算学生状态。"""
    now = now or datetime.utcnow()
    query = db.query(models.HealthRequest).filter(
        models.HealthRequest.status == "approved",
        models.HealthRequest.type.in_(["leave", "sick"]),
        models.HealthRequest.end_date.isnot(None),
        models.HealthRequest.end_date < now,
    )
    if student_id is not None:
        query = query.filter(models.HealthRequest.student_id == student_id)
    rows = query.all()
    affected = {row.student_id for row in rows}
    for row in rows:
        row.status = "ended"
        row.ended_at = now
        row.updated_at = now
    for affected_student_id in affected:
        recompute_student_health(db, affected_student_id, now)
    if rows:
        db.commit()
    return len(rows)


def health_request_dict(row: models.HealthRequest) -> dict:
    import json

    return {
        "id": row.id,
        "student_id": row.student_id,
        "type": row.type,
        "reason": row.reason,
        "start_date": row.start_date,
        "end_date": row.end_date,
        "attachments": json.loads(row.attachments) if row.attachments else [],
        "status": row.status,
        "reviewed_by": row.reviewed_by,
        "reviewed_at": row.reviewed_at,
        "review_comment": row.review_comment,
        "cancelled_at": row.cancelled_at,
        "ended_at": row.ended_at,
        "created_at": row.created_at,
        "updated_at": row.updated_at,
    }
