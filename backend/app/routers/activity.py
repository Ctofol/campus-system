from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
import math
from typing import Optional

from .. import models, schemas, auth, database, config
from ..services.score_service import verify_activity, get_sunshine_stats
from ..services.task_run_service import evaluate_task_run, student_may_submit_task
from ..services.face_verify_service import (
    apply_face_outcome_to_activity,
    verify_run_faces,
)
from ..services.test_analysis_service import enqueue_test_analysis, run_test_analysis_sync
from ..services.audit_service import record_audit

router = APIRouter(prefix="/activity", tags=["activity"])

get_db = database.get_db


@router.post("/{activity_id}/appeal")
def create_activity_appeal(
    activity_id: int,
    payload: schemas.ActivityAppealCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="仅学生可以提交运动申诉")
    act = db.query(models.Activity).filter(
        models.Activity.id == activity_id,
        models.Activity.user_id == current_user.id,
    ).first()
    if not act:
        raise HTTPException(status_code=404, detail="运动记录不存在")
    if act.is_valid or not (act.fail_reason or "").strip():
        raise HTTPException(status_code=409, detail="只有被判定异常的运动记录可以申诉")
    if db.query(models.ActivityAppeal).filter(models.ActivityAppeal.activity_id == activity_id).first():
        raise HTTPException(status_code=409, detail="该记录已经提交过申诉")
    appeal = models.ActivityAppeal(
        activity_id=activity_id,
        student_id=current_user.id,
        reason=payload.reason.strip(),
        status="pending",
    )
    db.add(appeal)
    record_audit(
        db,
        actor=current_user,
        action="activity_appeal.create",
        resource_type="activity",
        resource_id=activity_id,
        detail={"fail_reason": act.fail_reason},
    )
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="该记录已经提交过申诉")
    db.refresh(appeal)
    return {"id": appeal.id, "activity_id": activity_id, "status": appeal.status, "created_at": appeal.created_at}


@router.get("/appeals/me")
def list_my_activity_appeals(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="仅学生可以查看运动申诉")
    rows = db.query(models.ActivityAppeal).filter(
        models.ActivityAppeal.student_id == current_user.id
    ).order_by(models.ActivityAppeal.created_at.desc()).all()
    return [
        {
            "id": row.id,
            "activity_id": row.activity_id,
            "reason": row.reason,
            "status": row.status,
            "review_comment": row.review_comment,
            "created_at": row.created_at,
            "reviewed_at": row.reviewed_at,
        }
        for row in rows
    ]


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


def _apply_run_face_verify(act: models.Activity, user: models.User, db: Session) -> None:
    outcome = verify_run_faces(act.evidence, user=user, db=db)
    apply_face_outcome_to_activity(act, outcome)
    if not outcome.ok and config.FACE_BLOCK_ON_FAIL:
        act.is_valid = False
        act.fail_reason = outcome.reason or act.fail_reason


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

    exercise_type = metrics_data.pop("exercise_type", None)

    # 体测：不再随机评分，有视频则 pending 异步分析
    if activity_in.type == "test" and metrics_data.get("video_url"):
        metrics_data["count"] = metrics_data.get("count") or 0
        metrics_data["qualified"] = False
        metrics_data["score"] = None
        metrics_data["score_detail"] = None
        metrics_data["analysis_status"] = "pending"
        metrics_data["analysis_error"] = None
        metrics_data["exercise_type"] = exercise_type

    db_metrics = models.ActivityMetrics(
        activity_id=db_activity.id,
        **metrics_data,
    )
    if activity_in.type == "test" and metrics_data.get("video_url") and not db_metrics.exercise_type:
        db_metrics.exercise_type = exercise_type

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
            _apply_run_face_verify(db_activity, current_user, db)
        else:
            is_valid, fail_reason, face_verified = verify_activity(current_user, db_activity, db)
            db_activity.is_valid = is_valid
            db_activity.fail_reason = fail_reason or None
            db_activity.face_verified = face_verified
    else:
        if db_activity.source == "task" and db_activity.task_id:
            task = db.query(models.Task).filter(models.Task.id == db_activity.task_id).first()
            db_activity.is_valid = False
            db_activity.fail_reason = "视频分析中，请稍后查看结果"
            db_activity.face_verified = False
            if not db_metrics.video_url:
                ok, reason = True, None
                if task.min_count and int(task.min_count) > 0:
                    cnt = db_metrics.count or 0
                    if cnt < int(task.min_count):
                        ok = False
                        reason = f"次数未达标（需≥{task.min_count}次，实际{cnt}次）"
                db_activity.is_valid = ok
                db_activity.fail_reason = reason
        else:
            if db_metrics.video_url:
                db_activity.is_valid = False
                db_activity.fail_reason = "视频分析中，请稍后查看结果"
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

    if db_activity.type == "run" and db_activity.is_valid:
        distance = db_metrics.distance or 0
        if distance > 0:
            member = db.query(models.RunGroupMember).filter(
                models.RunGroupMember.user_id == current_user.id
            ).first()
            if member:
                member.total_mileage = (member.total_mileage or 0) + distance
                group = db.query(models.RunGroup).filter(
                    models.RunGroup.id == member.group_id
                ).first()
                if group:
                    group.total_mileage = (group.total_mileage or 0) + distance

    db.commit()
    db.refresh(db_activity)
    db.refresh(db_metrics)

    # Check medals after activity completion
    try:
        from .medal import _check_and_award
        _check_and_award(db, current_user.id)
    except Exception:
        pass

    if db_activity.type == "test" and db_metrics.video_url:
        if config.TEST_ANALYSIS_USE_BACKGROUND:
            enqueue_test_analysis(db_activity.id)
        else:
            run_test_analysis_sync(db_activity.id)
            db.refresh(db_activity)
            db.refresh(db_metrics)

    return _finish_response(db, db_activity, today_completed)


@router.get("/{activity_id}/analysis-status")
def get_analysis_status(
    activity_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    act = (
        db.query(models.Activity)
        .filter(
            models.Activity.id == activity_id,
            models.Activity.user_id == current_user.id,
        )
        .first()
    )
    if not act or not act.metrics:
        raise HTTPException(status_code=404, detail="记录不存在")
    m = act.metrics
    return {
        "activity_id": act.id,
        "type": act.type,
        "analysis_status": m.analysis_status or "success",
        "analysis_error": m.analysis_error,
        "count": m.count,
        "qualified": m.qualified,
        "score": m.score,
        "score_detail": m.score_detail,
        "exercise_type": m.exercise_type,
        "face_verified": act.face_verified,
        "face_match_score": act.face_match_score,
        "face_fail_code": act.face_fail_code,
        "face_detail": getattr(act, "face_detail", None),
        "is_valid": act.is_valid,
        "fail_reason": act.fail_reason,
    }


@router.post("/{activity_id}/reanalyze")
def reanalyze_test_activity(
    activity_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    act = (
        db.query(models.Activity)
        .filter(
            models.Activity.id == activity_id,
            models.Activity.user_id == current_user.id,
            models.Activity.type == "test",
        )
        .first()
    )
    if not act or not act.metrics or not act.metrics.video_url:
        raise HTTPException(status_code=404, detail="体测记录或视频不存在")
    act.metrics.analysis_status = "pending"
    act.metrics.analysis_error = None
    db.commit()
    if config.TEST_ANALYSIS_USE_BACKGROUND:
        enqueue_test_analysis(activity_id)
    else:
        run_test_analysis_sync(activity_id)
    db.refresh(act)
    db.refresh(act.metrics)
    return {
        "message": "已重新提交分析",
        "analysis_status": act.metrics.analysis_status,
    }


@router.get("/history", response_model=schemas.ActivityListResponse)
def get_history(
    page: int = 1,
    size: int = 20,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    from sqlalchemy.orm import joinedload
    from ..services.home_dashboard_service import enrich_activity_trajectory_fields

    query = db.query(models.Activity).filter(models.Activity.user_id == current_user.id)
    total = query.count()
    activities = (
        query.options(joinedload(models.Activity.metrics))
        .order_by(models.Activity.started_at.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    items = []
    for act in activities:
        base = schemas.ActivityOut.model_validate(act).model_dump()
        extra = enrich_activity_trajectory_fields(act)
        base["has_trajectory"] = extra["has_trajectory"]
        base["trajectory_preview"] = extra["trajectory_preview"]
        items.append(schemas.ActivityOut(**base))

    return {
        "items": items,
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
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="仅学生可以进行地点打卡")
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
        return {"success": False, "message": "不在打卡范围内", "distance": round(distance, 2)}

    now = datetime.utcnow()
    recent = db.query(models.CheckpointVisit).filter(
        models.CheckpointVisit.user_id == current_user.id,
        models.CheckpointVisit.checkpoint_id == checkpoint.id,
        models.CheckpointVisit.created_at >= now - timedelta(minutes=5),
    ).order_by(models.CheckpointVisit.created_at.desc()).first()
    if recent:
        return {
            "success": True,
            "message": "近期已完成打卡",
            "distance": recent.distance_m,
            "timestamp": recent.created_at,
            "visit_id": recent.id,
            "duplicate": True,
        }
    visit = models.CheckpointVisit(
        user_id=current_user.id,
        checkpoint_id=checkpoint.id,
        latitude=checkin_in.lat,
        longitude=checkin_in.lng,
        distance_m=round(distance, 2),
        created_at=now,
    )
    db.add(visit)
    db.commit()
    db.refresh(visit)
    return {
        "success": True,
        "message": "打卡成功",
        "distance": visit.distance_m,
        "timestamp": visit.created_at,
        "visit_id": visit.id,
        "duplicate": False,
    }


@router.get("/checkins/me")
def list_my_checkins(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="仅学生可以查看打卡记录")
    query = db.query(models.CheckpointVisit).filter(
        models.CheckpointVisit.user_id == current_user.id
    )
    total = query.count()
    rows = (
        query.order_by(models.CheckpointVisit.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )
    return {
        "items": [
            {
                "id": row.id,
                "checkpoint_id": row.checkpoint_id,
                "checkpoint_name": row.checkpoint.name if row.checkpoint else "未知打卡点",
                "distance": row.distance_m,
                "created_at": row.created_at,
            }
            for row in rows
        ],
        "total": total,
        "page": page,
        "size": size,
    }


@router.post("/score/recalc")
def recalculate_activity_score(
    payload: dict,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    """体测：重新触发视频分析（非随机改分）。"""
    activity_id = payload.get("activity_id")
    if not activity_id:
        raise HTTPException(status_code=400, detail="Must provide activity_id")

    act = (
        db.query(models.Activity)
        .filter(
            models.Activity.id == activity_id,
            models.Activity.user_id == current_user.id,
            models.Activity.type == "test",
        )
        .first()
    )
    if not act or not act.metrics or not act.metrics.video_url:
        raise HTTPException(status_code=404, detail="Activity or test video not found")

    act.metrics.analysis_status = "pending"
    act.metrics.analysis_error = None
    db.commit()
    if config.TEST_ANALYSIS_USE_BACKGROUND:
        enqueue_test_analysis(activity_id)
    else:
        run_test_analysis_sync(activity_id)
        db.refresh(act.metrics)

    return {
        "message": "已提交重新分析",
        "analysis_status": act.metrics.analysis_status,
        "score": act.metrics.score,
    }
