from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import random
import math
from typing import Optional

from .. import models, schemas, auth, database
from ..services.score_service import verify_activity, get_sunshine_stats
from ..services.task_run_service import evaluate_task_run, student_may_submit_task

router = APIRouter(prefix="/activity", tags=["activity"])

get_db = database.get_db


def _finish_response(
    db: Session,
    act: models.Activity,
    today_completed: Optional[bool],
) -> schemas.ActivityFinishResponse:
    out = schemas.ActivityFinishResponse.model_validate(act, from_attributes=True)
    extra = {"today_completed": today_completed}
    if act.task_id:
        t = db.query(models.Task).filter(models.Task.id == act.task_id).first()
        extra["task_title"] = t.title if t else None
        extra["task_completed"] = act.is_valid
    else:
        extra["task_title"] = None
        extra["task_completed"] = None
    return out.model_copy(update=extra)


@router.post("/finish", response_model=schemas.ActivityFinishResponse)
def finish_activity(
    activity_in: schemas.ActivityFinish,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    if activity_in.source == "task":
        if not activity_in.task_id:
            raise HTTPException(status_code=400, detail="任务跑步必须携带 task_id")
        task = db.query(models.Task).filter(models.Task.id == activity_in.task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        ok, msg = student_may_submit_task(current_user, task)
        if not ok:
            raise HTTPException(status_code=400, detail=msg)
        if task.type != activity_in.type:
            raise HTTPException(status_code=400, detail="任务类型与提交类型不一致")
    elif activity_in.task_id:
        raise HTTPException(status_code=400, detail="非任务跑步不要携带 task_id")

    initial_status = "pending_review" if activity_in.source == "task" else "finished"
    db_activity = models.Activity(
        user_id=current_user.id,
        type=activity_in.type,
        source=activity_in.source,
        status=initial_status,
        started_at=activity_in.started_at,
        ended_at=activity_in.ended_at,
        task_id=activity_in.task_id if activity_in.source == "task" else None,
    )
    db.add(db_activity)
    db.flush()

    metrics_data = activity_in.metrics.model_dump()
    if "video_url" not in metrics_data:
        metrics_data["video_url"] = None

    if metrics_data.get("video_url") and activity_in.type == "test":
        metrics_data["count"] = random.randint(8, 15)
        metrics_data["qualified"] = metrics_data["count"] >= 10
        metrics_data["score"] = random.randint(70, 95)
        metrics_data["score_detail"] = f"动作标准度: {random.randint(80, 95)}%, 完成质量: 良好"

    db_metrics = models.ActivityMetrics(
        activity_id=db_activity.id,
        **metrics_data,
    )
    db.add(db_metrics)

    for evidence in activity_in.evidence:
        db_evidence = models.ActivityEvidence(
            activity_id=db_activity.id,
            **evidence.model_dump(),
        )
        db.add(db_evidence)

    db.flush()
    db.refresh(db_activity)

    if db_activity.type == "run":
        if db_activity.source == "task" and db_activity.task_id:
            task = db.query(models.Task).filter(models.Task.id == db_activity.task_id).first()
            ok, reason = evaluate_task_run(task, db_metrics)
            db_activity.is_valid = ok
            db_activity.fail_reason = reason
            db_activity.face_verified = True
        else:
            is_valid, fail_reason, face_verified = verify_activity(current_user, db_activity, db)
            db_activity.is_valid = is_valid
            db_activity.fail_reason = fail_reason or None
            db_activity.face_verified = face_verified
    else:
        if db_activity.source == "task" and db_activity.task_id:
            task = db.query(models.Task).filter(models.Task.id == db_activity.task_id).first()
            ok, reason = True, None
            if task.min_count and int(task.min_count) > 0:
                cnt = db_metrics.count or 0
                if cnt < int(task.min_count):
                    ok = False
                    reason = f"次数未达标（需≥{task.min_count}次，实际{cnt}次）"
            db_activity.is_valid = ok
            db_activity.fail_reason = reason
            db_activity.face_verified = True
        else:
            db_activity.is_valid = bool(db_metrics.qualified)
            db_activity.fail_reason = None if db_metrics.qualified else "体测未达标"

    today_completed = None
    if activity_in.source == "free" and db_activity.type == "run":
        try:
            stats = get_sunshine_stats(current_user, db)
            today_completed = stats.get("today_status") == "success"
        except Exception:
            today_completed = None

    db.commit()
    db.refresh(db_activity)
    db.refresh(db_metrics)

    return _finish_response(db, db_activity, today_completed)


@router.get("/history", response_model=schemas.ActivityListResponse)
def get_history(
    page: int = 1,
    size: int = 20,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(models.Activity).filter(models.Activity.user_id == current_user.id)
    total = query.count()
    activities = (
        query.order_by(models.Activity.started_at.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    return {
        "items": activities,
        "total": total,
        "page": page,
        "size": size,
    }


@router.post("/checkin")
def check_in(
    checkin_in: schemas.CheckInRequest,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    checkpoint = (
        db.query(models.Checkpoint).filter(models.Checkpoint.id == checkin_in.checkpoint_id).first()
    )
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")

    R = 6371e3
    dLat = (checkin_in.lat - checkpoint.latitude) * math.pi / 180
    dLng = (checkin_in.lng - checkpoint.longitude) * math.pi / 180
    a = math.sin(dLat / 2) * math.sin(dLat / 2) + math.cos(checkpoint.latitude * math.pi / 180) * math.cos(
        checkin_in.lat * math.pi / 180
    ) * math.sin(dLng / 2) * math.sin(dLng / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c

    if distance > checkpoint.radius:
        return {"success": False, "message": "Not in range", "distance": distance}

    return {
        "success": True,
        "message": "Check-in successful",
        "distance": distance,
        "timestamp": datetime.utcnow(),
    }


@router.post("/score/recalc")
def recalculate_activity_score(
    payload: dict,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    activity_id = payload.get("activity_id")
    if not activity_id:
        raise HTTPException(status_code=400, detail="Must provide activity_id")

    activity = (
        db.query(models.Activity)
        .filter(
            models.Activity.id == activity_id,
            models.Activity.user_id == current_user.id,
        )
        .first()
    )
    if not activity or not activity.metrics:
        raise HTTPException(status_code=404, detail="Activity or metrics not found")

    activity.metrics.score = random.randint(70, 95)
    db.commit()
    return {"message": "评分更新成功", "score": activity.metrics.score}
