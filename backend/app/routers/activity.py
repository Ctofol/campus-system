from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import random
import math
from .. import models, schemas, auth, database
from ..services.score_service import verify_activity, get_sunshine_stats

router = APIRouter(prefix="/activity", tags=["activity"])

get_db = database.get_db

@router.post("/finish", response_model=schemas.ActivityOut)
def finish_activity(
    activity_in: schemas.ActivityFinish,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    initial_status = "pending_review" if activity_in.source == "task" else "finished"
    db_activity = models.Activity(
        user_id=current_user.id,
        type=activity_in.type,
        source=activity_in.source,
        status=initial_status,
        started_at=activity_in.started_at,
        ended_at=activity_in.ended_at
    )
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)

    metrics_data = activity_in.metrics.dict()
    if 'video_url' not in metrics_data:
        metrics_data['video_url'] = None
    
    # 模拟AI评分逻辑
    if metrics_data.get('video_url') and activity_in.type == "test":
        metrics_data['count'] = random.randint(8, 15)
        metrics_data['qualified'] = metrics_data['count'] >= 10
        metrics_data['score'] = random.randint(70, 95)
        metrics_data['score_detail'] = f"动作标准度: {random.randint(80, 95)}%, 完成质量: 良好"
    
    db_metrics = models.ActivityMetrics(
        activity_id=db_activity.id,
        **metrics_data
    )
    db.add(db_metrics)

    for evidence in activity_in.evidence:
        db_evidence = models.ActivityEvidence(
            activity_id=db_activity.id,
            **evidence.dict()
        )
        db.add(db_evidence)
    
    # 阳光跑自动审核
    if db_activity.type == "run":
        is_valid, fail_reason, face_verified = verify_activity(current_user, db_activity, db)
        db_activity.is_valid = is_valid
        db_activity.fail_reason = fail_reason or None
        db_activity.face_verified = face_verified
        db.commit()
        db.refresh(db_activity)
    else:
        db.commit()
        db.refresh(db_activity)

    # 达标状态统计提示
    try:
        stats = get_sunshine_stats(current_user, db)
        setattr(db_activity, "today_completed", stats.get("today_status") == "success")
    except Exception:
        setattr(db_activity, "today_completed", None)

    return db_activity

@router.get("/history", response_model=schemas.ActivityListResponse)
def get_history(
    page: int = 1,
    size: int = 20,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(models.Activity).filter(models.Activity.user_id == current_user.id)
    total = query.count()
    activities = query.order_by(models.Activity.started_at.desc()).offset((page - 1) * size).limit(size).all()
    
    return {
        "items": activities,
        "total": total,
        "page": page,
        "size": size
    }

@router.post("/checkin")
def check_in(
    checkin_in: schemas.CheckInRequest,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    checkpoint = db.query(models.Checkpoint).filter(models.Checkpoint.id == checkin_in.checkpoint_id).first()
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")
        
    R = 6371e3
    dLat = (checkin_in.lat - checkpoint.latitude) * math.pi / 180
    dLng = (checkin_in.lng - checkpoint.longitude) * math.pi / 180
    a = math.sin(dLat/2) * math.sin(dLat/2) + \
        math.cos(checkpoint.latitude * math.pi / 180) * math.cos(checkin_in.lat * math.pi / 180) * \
        math.sin(dLng/2) * math.sin(dLng/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    
    if distance > checkpoint.radius:
        return {"success": False, "message": "Not in range", "distance": distance}
        
    return {"success": True, "message": "Check-in successful", "distance": distance, "timestamp": datetime.utcnow()}

@router.post("/score/recalc")
def recalculate_activity_score(
    payload: dict,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    activity_id = payload.get('activity_id')
    if not activity_id:
        raise HTTPException(status_code=400, detail="Must provide activity_id")
    
    activity = db.query(models.Activity).filter(
        models.Activity.id == activity_id,
        models.Activity.user_id == current_user.id
    ).first()
    if not activity or not activity.metrics:
        raise HTTPException(status_code=404, detail="Activity or metrics not found")
    
    # 模拟重新评分
    activity.metrics.score = random.randint(70, 95)
    db.commit()
    return {"message": "评分更新成功", "score": activity.metrics.score}
