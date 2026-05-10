from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List
from datetime import datetime, timedelta
from .. import models, schemas, auth
from ..database import get_db
from ..services.task_run_service import student_may_submit_task

router = APIRouter(prefix="/student", tags=["student"])

@router.get("/summary")
async def get_student_summary(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Get student's today summary statistics - only for current user"""
    
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can access this endpoint")
    
    # Get today's activities for CURRENT USER ONLY
    today = datetime.utcnow().date()
    today_start = datetime(today.year, today.month, today.day)
    
    activities = db.query(models.Activity).filter(
        models.Activity.user_id == current_user.id,  # 只查询当前用户
        models.Activity.started_at >= today_start
    ).all()
    
    # Calculate totals
    total_calories = 0
    total_duration = 0  # in seconds
    total_distance = 0.0  # in km
    
    for activity in activities:
        if activity.metrics:
            # Estimate calories (rough calculation: 1km running = ~60 kcal)
            if activity.metrics.distance:
                total_distance += activity.metrics.distance
                total_calories += int(activity.metrics.distance * 60)
            
            if activity.metrics.duration:
                total_duration += activity.metrics.duration
    
    # Convert duration to minutes
    total_minutes = total_duration // 60
    
    # Get pending tasks count for current user
    # 如果学生还没有班级，不展示任何待办任务
    if current_user.class_id is None:
        pending_tasks = 0
    else:
        pending_tasks = (
            db.query(models.Task)
            .filter(
                or_(
                    models.Task.class_id == current_user.class_id,
                    and_(models.Task.target_group == "all", models.Task.class_id.is_(None)),
                )
            )
            .filter(models.Task.deadline >= datetime.utcnow())
            .count()
        )
    
    return {
        "user_id": current_user.id,  # 添加用户ID用于调试
        "user_name": current_user.name,  # 添加用户名用于调试
        "today_minutes": total_minutes,
        "calories": total_calories,
        "distance": round(total_distance, 2),
        "todo_count": pending_tasks,
        "activity_count": len(activities)  # 添加活动数量用于调试
    }

@router.get("/total-stats")
async def get_total_stats(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Get student's total exercise statistics"""
    
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can access this endpoint")
    
    # Query all activities for current user
    activities = db.query(models.Activity).filter(
        models.Activity.user_id == current_user.id,
        models.Activity.type == "run"
    ).all()
    
    total_distance = 0.0  # in meters
    total_duration = 0  # in seconds
    total_calories = 0
    
    for activity in activities:
        if activity.metrics:
            if activity.metrics.distance:
                total_distance += activity.metrics.distance
            if activity.metrics.duration:
                total_duration += activity.metrics.duration
    
    # Calculate calories (rough estimation: 1km = 60 kcal)
    total_calories = int((total_distance / 1000) * 60)
    
    return {
        "total_distance": round(total_distance / 1000, 1),  # Convert to km
        "total_duration": round(total_duration / 60),  # Convert to minutes
        "total_calories": total_calories,
        "total_count": len(activities)
    }

@router.get("/tasks")
async def get_student_tasks(
    page: int = 1,
    size: int = 20,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Get student's assigned tasks"""
    
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can access this endpoint")
    
    # 如果学生还没有班级，则不返回任何任务
    if current_user.class_id is None:
        return {
            "items": [],
            "total": 0,
            "page": page,
            "size": size
        }
    
    query = db.query(models.Task).filter(
        or_(
            models.Task.class_id == current_user.class_id,
            and_(models.Task.target_group == "all", models.Task.class_id.is_(None)),
        )
    ).order_by(models.Task.deadline.asc())

    total = query.count()
    tasks = query.offset((page - 1) * size).limit(size).all()
    now = datetime.utcnow()

    result_tasks = []
    for task in tasks:
        last_act = (
            db.query(models.Activity)
            .filter(
                models.Activity.user_id == current_user.id,
                models.Activity.task_id == task.id,
                models.Activity.source == "task",
                models.Activity.type == task.type,
                models.Activity.started_at >= task.created_at,
            )
            .order_by(models.Activity.started_at.desc())
            .first()
        )

        expired = bool(task.deadline and task.deadline < now)
        not_started = bool(task.starts_at and now < task.starts_at)
        if last_act and last_act.is_valid:
            st = "completed"
        elif expired:
            st = "expired"
        elif not_started:
            st = "not_started"
        elif last_act and not last_act.is_valid:
            st = "failed"
        else:
            st = "pending"

        time_left = task.deadline - now if task.deadline else None
        is_urgent = bool(
            time_left and time_left < timedelta(hours=24) and st in ("pending", "failed")
        )

        result_tasks.append(
            {
                "id": task.id,
                "title": task.title,
                "type": "run" if task.type == "run" else "learn",
                "starts_at": task.starts_at.isoformat() if task.starts_at else None,
                "deadline": task.deadline.isoformat() if task.deadline else None,
                "urgent": is_urgent,
                "status": st,
                "description": task.description,
                "min_distance": task.min_distance,
                "min_duration": task.min_duration,
                "min_count": task.min_count,
            }
        )
    
    return {
        "items": result_tasks,
        "total": total,
        "page": page,
        "size": size
    }


@router.get("/tasks/{task_id}")
def get_student_task_detail(
    task_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    """任务跑步页拉取要求（专项跑中间页展示）"""
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students")

    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if current_user.class_id is None:
        raise HTTPException(status_code=403, detail="未分班，无法领取任务")

    allowed = (task.class_id == current_user.class_id) or (
        task.target_group == "all" and task.class_id is None
    )
    if not allowed:
        raise HTTPException(status_code=403, detail="无权查看该任务")

    may, hint = student_may_submit_task(current_user, task)
    return {
        "id": task.id,
        "title": task.title,
        "type": task.type,
        "description": task.description,
        "starts_at": task.starts_at.isoformat() if task.starts_at else None,
        "deadline": task.deadline.isoformat() if task.deadline else None,
        "min_distance": task.min_distance,
        "min_duration": task.min_duration,
        "min_count": task.min_count,
        "class_id": task.class_id,
        "can_submit": may,
        "submit_hint": hint,
    }


@router.get("/task-runs/history")
def get_student_task_run_history(
    page: int = 1,
    size: int = 20,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    """我的：任务跑步/任务体测提交历史（与阳光跑区分）"""
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students")

    q = (
        db.query(models.Activity)
        .filter(
            models.Activity.user_id == current_user.id,
            models.Activity.source == "task",
            models.Activity.task_id.isnot(None),
        )
        .order_by(models.Activity.started_at.desc())
    )
    total = q.count()
    rows = q.offset((page - 1) * size).limit(size).all()
    out = []
    for act in rows:
        t = db.query(models.Task).filter(models.Task.id == act.task_id).first()
        m = act.metrics
        out.append(
            {
                "activity_id": act.id,
                "task_id": act.task_id,
                "task_title": t.title if t else "",
                "task_type": act.type,
                "started_at": act.started_at,
                "ended_at": act.ended_at,
                "completed_ok": act.is_valid,
                "fail_reason": act.fail_reason,
                "distance_km": m.distance if m else None,
                "duration_sec": m.duration if m else None,
                "pace": m.pace if m else None,
            }
        )
    return {"items": out, "total": total, "page": page, "size": size}


@router.get("/sunshine-stats")
def get_sunshine_dashboard(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """
    阳光跑看板数据：
    - total_valid_count: 历史达标次数
    - score: 阶梯计分
    - today_status: 'not_started' | 'success' | 'failed'
    - today_fail_reason: 最近一次失败原因
    """
    from ..services.score_service import get_sunshine_stats
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can access sunshine stats")

    return get_sunshine_stats(current_user, db)

@router.post("/health/request")
def create_health_request(
    request_in: schemas.HealthRequestCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can submit health requests")
        
    # Check if there is already a pending request
    pending = db.query(models.HealthRequest).filter(
        models.HealthRequest.student_id == current_user.id,
        models.HealthRequest.status == "pending"
    ).first()
    
    if pending:
        raise HTTPException(status_code=400, detail="You already have a pending request")
    
    import json
    attachments_json = json.dumps(request_in.attachments) if request_in.attachments else None
        
    # 校验请假时间（仅请假类型需要）
    start_date = request_in.start_date
    end_date = request_in.end_date
    if request_in.type == "leave":
        if not start_date or not end_date:
            raise HTTPException(status_code=400, detail="Leave requests must include start_date and end_date")
        if end_date < start_date:
            raise HTTPException(status_code=400, detail="end_date must be after start_date")

    new_req = models.HealthRequest(
        student_id=current_user.id,
        type=request_in.type,
        reason=request_in.reason,
        attachments=attachments_json,
        start_date=start_date,
        end_date=end_date,
        status="pending"
    )
    db.add(new_req)
    db.commit()
    db.refresh(new_req)
    
    return {
        "id": new_req.id,
        "student_id": new_req.student_id,
        "type": new_req.type,
        "reason": new_req.reason,
        "start_date": new_req.start_date,
        "end_date": new_req.end_date,
        "attachments": json.loads(new_req.attachments) if new_req.attachments else [],
        "status": new_req.status,
        "created_at": new_req.created_at,
        "updated_at": new_req.updated_at
    }

@router.get("/health/requests")
def get_my_health_requests(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    import json
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can view their health requests")
        
    requests = db.query(models.HealthRequest).filter(
        models.HealthRequest.student_id == current_user.id
    ).order_by(models.HealthRequest.created_at.desc()).all()
    
    result = []
    for req in requests:
        result.append({
            "id": req.id,
            "student_id": req.student_id,
            "type": req.type,
            "reason": req.reason,
            "start_date": req.start_date,
            "end_date": req.end_date,
            "attachments": json.loads(req.attachments) if req.attachments else [],
            "status": req.status,
            "created_at": req.created_at,
            "updated_at": req.updated_at
        })
    return result
