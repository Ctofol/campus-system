from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import json
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
            .filter(models.Task.class_id == current_user.class_id)
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
    
    total_distance_km = 0.0
    total_duration = 0
    total_calories = 0

    for activity in activities:
        if activity.metrics:
            if activity.metrics.distance:
                d = float(activity.metrics.distance)
                total_distance_km += d / 1000.0 if d > 100 else d
            if activity.metrics.duration:
                total_duration += activity.metrics.duration

    total_calories = int(total_distance_km * 60)

    return {
        "total_distance": round(total_distance_km, 1),
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
    
    query = (
        db.query(models.Task)
        .filter(models.Task.class_id == current_user.class_id)
        .order_by(models.Task.deadline.asc())
    )

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

    if task.class_id != current_user.class_id:
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


@router.get("/home/dashboard", response_model=schemas.HomeDashboardOut)
def get_home_dashboard(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    """学生首页：累计里程、本周数据、最近活动（含轨迹预览）、目标、未读通知。"""
    from ..services.home_dashboard_service import get_home_dashboard as build_home_dashboard

    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can access home dashboard")
    try:
        return build_home_dashboard(current_user, db)
    except ValueError:
        raise HTTPException(status_code=403, detail="Only students can access home dashboard")


@router.put("/home/run-goal")
def update_weekly_run_goal(
    body: schemas.RunGoalUpdate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    """保存学生本周跑步目标（公里）；传 0 表示清除。"""
    from ..services.home_dashboard_service import set_weekly_run_goal

    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can set run goal")
    km = set_weekly_run_goal(current_user, float(body.weekly_goal_km or 0), db)
    return {"success": True, "weekly_run_goal_km": km}


@router.get("/weather", response_model=schemas.WeatherResponse)
def get_weather(
    lat: float = Query(..., description="纬度 GCJ-02"),
    lng: float = Query(..., description="经度 GCJ-02"),
    current_user: models.User = Depends(auth.get_current_user),
):
    """首页天气：服务端代理腾讯位置服务，前端仅传经纬度。"""
    from ..services.weather_service import get_realtime_weather

    if lat < -90 or lat > 90 or lng < -180 or lng > 180:
        raise HTTPException(status_code=400, detail="无效的经纬度")
    result = get_realtime_weather(lat, lng)
    return schemas.WeatherResponse(
        ok=bool(result.get("ok")),
        weather=result.get("weather"),
        error=result.get("error"),
        message=result.get("message"),
    )


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


@router.get("/checkin-calendar")
def get_checkin_calendar(
    year: int = None,
    month: int = None,
    selected_day: int = None,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """
    打卡日历数据（按月）：
    返回指定月份每天是否有有效阳光跑打卡，以及统计数据。
    """
    from ..services.score_service import get_sunshine_stats, sunshine_run_filter
    from datetime import datetime, date, timedelta
    import calendar as cal_module

    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can access calendar")

    today = date.today()
    if not year:
        year = today.year
    if not month:
        month = today.month

    # 该月第一天和最后一天
    first_day = date(year, month, 1)
    last_day = date(year, month, cal_module.monthrange(year, month)[1])

    # 查询该月所有有效阳光跑
    month_activities = (
        db.query(models.Activity)
        .filter(
            models.Activity.user_id == current_user.id,
            models.Activity.is_valid.is_(True),
            models.Activity.started_at >= datetime(year, month, 1),
            models.Activity.started_at < datetime(year, month, last_day.day, 23, 59, 59),
        )
        .filter(sunshine_run_filter())
        .order_by(models.Activity.started_at.asc())
        .all()
    )

    # 构建打卡日期集合
    checkin_dates = set()
    for act in month_activities:
        checkin_dates.add(act.started_at.date().day)

    # 本月打卡天数
    month_count = len(checkin_dates)

    # 连续打卡天数（从今天往前算）
    streak = 0
    check_date = today
    while True:
        has_valid = (
            db.query(models.Activity)
            .filter(
                models.Activity.user_id == current_user.id,
                models.Activity.is_valid.is_(True),
                models.Activity.started_at >= datetime(check_date.year, check_date.month, check_date.day),
                models.Activity.started_at < datetime(check_date.year, check_date.month, check_date.day, 23, 59, 59),
            )
            .filter(sunshine_run_filter())
            .count()
        )
        if has_valid:
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break

    # 累计打卡天数（历史所有有效记录的不重复天数）
    all_valid = (
        db.query(models.Activity)
        .filter(
            models.Activity.user_id == current_user.id,
            models.Activity.is_valid.is_(True),
        )
        .filter(sunshine_run_filter())
        .all()
    )
    total_days = len(set(a.started_at.date() for a in all_valid))

    # 选中日期的打卡记录（默认今日，或传入的 selected_day）
    if selected_day:
        sel_day = selected_day
    elif year == today.year and month == today.month:
        sel_day = today.day
    else:
        sel_day = last_day.day
    selected_activities = [
        a for a in month_activities
        if a.started_at.date().day == sel_day
    ]
    selected_records = []
    for act in selected_activities:
        m = act.metrics
        selected_records.append({
            "id": act.id,
            "started_at": act.started_at.isoformat(),
            "distance_km": round(m.distance, 2) if m and m.distance else 0,
            "duration": m.duration if m else 0,
            "pace": m.pace if m else None,
            "is_valid": bool(act.is_valid),
        })

    return {
        "year": year,
        "month": month,
        "checkin_days": sorted(list(checkin_dates)),
        "month_count": month_count,
        "streak": streak,
        "total_days": total_days,
        "today": today.day if year == today.year and month == today.month else None,
        "selected_day": sel_day,
        "selected_records": selected_records,
    }

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


@router.get("/notifications", response_model=List[schemas.UserNotificationOut])
def list_my_notifications(
    unread_only: bool = Query(False),
    ntype: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(models.UserNotification).filter(
        models.UserNotification.user_id == current_user.id
    )
    if unread_only:
        q = q.filter(models.UserNotification.is_read.is_(False))
    if ntype:
        q = q.filter(models.UserNotification.ntype == ntype)
    rows = (
        q.order_by(models.UserNotification.created_at.desc())
        .limit(limit)
        .all()
    )
    return rows


@router.get("/notifications/unread-count", response_model=schemas.UserNotificationUnread)
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


@router.put("/notifications/{notification_id}/read")
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


@router.put("/notifications/read-all")
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
