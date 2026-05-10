from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, desc
from typing import List
import io
import csv
from datetime import datetime, timedelta
from .. import models, schemas, auth
from ..services.teacher_service import get_teacher_stats_data, get_managed_students_query
from ..services.score_service import calculate_total_score, sunshine_run_filter
from ..database import get_db

router = APIRouter(prefix="/teacher", tags=["teacher"])

async def _get_teacher_stats_data(current_user: models.User, db: Session):
    """教师端统计逻辑：委托给 teacher_service 处理"""
    try:
        from ..services.teacher_service import get_teacher_stats_data
        return await get_teacher_stats_data(current_user, db)
    except Exception as e:
        print(f"Error in stats delegation: {e}")
        # Return something to avoid crash
        return {
            "student_count": 0, "today_checkin": 0, "abnormal_count": 0,
            "pending_approvals": 0, "pending_health": 0, "pending_activities": 0,
            "avg_pace": "--", "task_count": 0, "compliance_rate": 0,
            "qualified_rate": 0, "completion_rate": 0
        }

def _legacy_stats_marker():
    pass


@router.get("/stats", response_model=schemas.TeacherStatsOut)
async def get_teacher_stats(
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    """获取教师端平铺统计数据（适配管理页、学员页）"""
    stats_data = await _get_teacher_stats_data(current_user, db)
    return stats_data

@router.get("/dashboard/stats", response_model=schemas.TeacherDashboardOut)
async def get_teacher_dashboard_stats(
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    """获取教师端工作台聚合统计数据（适配首页）"""
    stats_data = await _get_teacher_stats_data(current_user, db)
    
    # 构造待办事项 (分拆显示，避免数据混淆)
    todos = []
    if stats_data.get("pending_health", 0) > 0:
        todos.append({
            "id": "health_pending",
            "title": f"有 {stats_data['pending_health']} 条请假/伤病待审批",
            "type": "health",
            "desc": "请及时处理学生的申请",
            "path": "/pages/teacher/students/students",
            "time": "今日"
        })
    
    if stats_data.get("pending_activities", 0) > 0:
        todos.append({
            "id": "activity_pending",
            "title": f"有 {stats_data['pending_activities']} 条运动异常需核实",
            "type": "exception",
            "desc": "可能存在代跑或数据异常",
            "path": "/pages/teacher/exceptions/exceptions",
            "time": "今日"
        })
    
    return {"stats": stats_data, "todos": todos}

@router.get("/weekly-trend")
async def get_weekly_trend(
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    """Get weekly activity trend data - unified management"""
    days = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    trend_data = []
    
    student_query = await get_managed_students_query(current_user, db)
    managed_student_ids = [u.id for u in student_query.with_entities(models.User.id).all()]
    
    if not managed_student_ids:
        # No students, return empty trend
        for i in range(6, -1, -1):
            date = datetime.utcnow() - timedelta(days=i)
            trend_data.append({
                "day": days[(date.weekday()) % 7],
                "val": 0,
                "color": "linear-gradient(180deg, #e0e0e0 0%, #f5f5f5 100%)",
                "count": 0
            })
        return trend_data
    
    # Get activities for the past 7 days from managed students
    for i in range(6, -1, -1):
        date = datetime.utcnow() - timedelta(days=i)
        day_start = datetime(date.year, date.month, date.day)
        day_end = day_start + timedelta(days=1)
        
        count = (
            db.query(models.Activity)
            .filter(
                models.Activity.started_at >= day_start,
                models.Activity.started_at < day_end,
                models.Activity.user_id.in_(managed_student_ids),
            )
            .filter(sunshine_run_filter())
            .count()
        )
        
        # Calculate percentage (max 100)
        percentage = min(int(count / (len(managed_student_ids) * 0.5 + 1) * 100), 100) if count > 0 else 0
        
        # Determine color based on activity level
        if percentage >= 70:
            color = "linear-gradient(180deg, #20C997 0%, #63e6be 100%)"
        elif percentage >= 40:
            color = "linear-gradient(180deg, #4dabf7 0%, #74c0fc 100%)"
        else:
            color = "linear-gradient(180deg, #e0e0e0 0%, #f5f5f5 100%)"
        
        trend_data.append({
            "day": days[(date.weekday()) % 7],
            "val": percentage,
            "color": color,
            "count": count
        })
    
    return trend_data

@router.get("/classes")
async def get_teacher_classes(
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    """返回所有班级（适配前端请求）"""
    classes = db.query(models.Class).all()
    results = []
    for c in classes:
        results.append({
            "id": c.id,
            "name": f"{c.major.name if c.major else ''} {c.name}".strip(),
            "student_count": len(c.students)
        })
    return results

@router.get("/health/requests")
async def get_health_requests_v2(
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    """适配前端请求：获取请假/异常审批列表（统一管理逻辑）"""
    student_query = await get_managed_students_query(current_user, db)
    managed_student_ids = [u.id for u in student_query.with_entities(models.User.id).all()]
    
    if not managed_student_ids:
        return []
        
    pending_requests = db.query(models.HealthRequest).filter(
        models.HealthRequest.status == "pending",
        models.HealthRequest.student_id.in_(managed_student_ids)
    ).all()
    
    return [
        {
            "id": req.id,
            "student_name": req.student.name if req.student else "未知",
            "type": req.type,
            "reason": req.reason,
            "start_date": req.start_date,
            "end_date": req.end_date,
            "created_at": req.created_at
        } for req in pending_requests
    ]


@router.get("/weekly-sunshine-trend")
async def get_weekly_sunshine_trend(
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    """适配前端请求：本周阳光跑趋势（统一管理）"""
    days_map = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    res = []
    
    student_query = await get_managed_students_query(current_user, db)
    managed_student_ids = [u.id for u in student_query.with_entities(models.User.id).all()]
    
    for i in range(6, -1, -1):
        date = datetime.utcnow() - timedelta(days=i)
        day_start = datetime(date.year, date.month, date.day)
        day_end = day_start + timedelta(days=1)
        
        count = 0
        if managed_student_ids:
            count = (
                db.query(models.Activity)
                .filter(
                    models.Activity.started_at >= day_start,
                    models.Activity.started_at < day_end,
                    models.Activity.user_id.in_(managed_student_ids),
                )
                .filter(sunshine_run_filter())
                .count()
            )
            
        res.append({
            "day": days_map[date.weekday()],
            "value": count
        })
    return res

@router.get("/students/abnormal")
async def get_abnormal_students(
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    """适配前端请求：获取状态异常的学生（统一管理）"""
    student_query = await get_managed_students_query(current_user, db)
    
    students = student_query.filter(
        models.User.health_status != "normal"
    ).all()
    
    return students

@router.get("/class/{class_id}/analysis", response_model=schemas.ClassAnalysisOut)
async def get_class_analysis(
    class_id: int,
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    """Get class analysis data（权限：TeacherClass 绑定班级）"""
    # Get students in this class within teacher's scope
    student_query = await get_managed_students_query(current_user, db)
    students = student_query.filter(
        models.User.class_id == class_id
    ).all()
    
    student_count = len(students)
    
    cls_row = db.query(models.Class).filter(models.Class.id == class_id).first()
    class_name_display = (
        f"{cls_row.major.name if cls_row and cls_row.major else ''} {cls_row.name if cls_row else ''}".strip()
        or f"Class_{class_id}"
    )

    if student_count == 0:
        return {
            "class_id": class_id,
            "class_name": class_name_display,
            "student_count": 0,
            "avg_distance": 0.0,
            "avg_duration": 0,
            "completion_rate": 0.0
        }
    
    # Calculate averages from activities（仅阳光跑跑步记录）
    student_ids = [s.id for s in students]
    
    activities = (
        db.query(models.Activity)
        .filter(models.Activity.user_id.in_(student_ids))
        .filter(sunshine_run_filter())
        .all()
    )
    
    total_distance = 0.0
    total_duration = 0
    activity_count = 0
    
    for activity in activities:
        if activity.metrics:
            if activity.metrics.distance:
                total_distance += activity.metrics.distance
            if activity.metrics.duration:
                total_duration += activity.metrics.duration
            activity_count += 1
    
    avg_distance = total_distance / activity_count if activity_count > 0 else 0.0
    avg_duration = total_duration // activity_count if activity_count > 0 else 0
    
    # Completion rate: students with at least one activity
    students_with_activity = len(set(a.user_id for a in activities))
    completion_rate = (students_with_activity / student_count * 100) if student_count > 0 else 0.0
    
    return {
        "class_id": class_id,
        "class_name": class_name_display,
        "student_count": student_count,
        "avg_distance": round(avg_distance, 2),
        "avg_duration": avg_duration,
        "completion_rate": round(completion_rate, 2)
    }


@router.get("/class-member-details")
async def get_class_member_sunshine_details(
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db),
):
    """
    班级阳光跑积分排行（教师端 class-rank 页）。
    口径与学生端 /student/sunshine-stats 一致。
    """
    student_query = await get_managed_students_query(current_user, db)
    students = student_query.all()
    week_start = datetime.utcnow() - timedelta(days=7)

    items = []
    for s in students:
        valid_total = (
            db.query(func.count(models.Activity.id))
            .filter(
                models.Activity.user_id == s.id,
                models.Activity.is_valid.is_(True),
            )
            .filter(sunshine_run_filter())
            .scalar()
            or 0
        )
        weekly_valid = (
            db.query(func.count(models.Activity.id))
            .filter(
                models.Activity.user_id == s.id,
                models.Activity.is_valid.is_(True),
                models.Activity.started_at >= week_start,
            )
            .filter(sunshine_run_filter())
            .scalar()
            or 0
        )
        items.append(
            {
                "user_id": s.id,
                "student_id": s.student_id,
                "name": s.name,
                "class_name": s.class_name,
                "weekly_count": weekly_valid,
                "total_score": calculate_total_score(int(valid_total)),
            }
        )

    items.sort(key=lambda x: x["total_score"], reverse=True)
    return {"items": items}


@router.get("/student/{student_id}/activities")
async def list_student_activities_for_teacher(
    student_id: int,
    page: int = 1,
    size: int = 50,
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db),
):
    """学员跑步/体测记录（含任务跑与阳光跑），供教师学员详情页使用。"""
    student_query = await get_managed_students_query(current_user, db)
    stu = student_query.filter(models.User.id == student_id).first()
    if not stu:
        raise HTTPException(status_code=404, detail="学员不存在或无权限")

    q = db.query(models.Activity).filter(models.Activity.user_id == student_id)
    total = q.count()
    rows = (
        q.order_by(desc(models.Activity.started_at))
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    def metrics_dict(m):
        if not m:
            return None
        return {
            "id": m.id,
            "distance": m.distance,
            "duration": m.duration,
            "pace": m.pace,
            "trajectory": m.trajectory,
            "count": m.count,
            "qualified": m.qualified,
            "step_count": m.step_count,
            "video_url": m.video_url,
            "score": m.score,
            "teacher_score": m.teacher_score,
        }

    items = []
    for a in rows:
        m = a.metrics
        items.append(
            {
                "id": a.id,
                "user_id": a.user_id,
                "type": a.type,
                "source": a.source,
                "status": a.status,
                "task_id": a.task_id,
                "started_at": a.started_at,
                "ended_at": a.ended_at,
                "is_valid": a.is_valid,
                "fail_reason": a.fail_reason,
                "metrics": metrics_dict(m),
                "student_name": stu.name,
            }
        )

    return {"items": items, "total": total, "page": page, "size": size}


@router.get("/students", response_model=List[schemas.StudentDetail])
async def get_teacher_students(
    page: int = 1,
    size: int = 20,
    class_id: int = None,
    name: str = None,
    student_id: str = None,
    status: str = None,
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    """Get all students managed by the teacher (Unified logic)."""
    student_query = await get_managed_students_query(current_user, db)
    query = student_query
    
    if class_id:
        query = query.filter(models.User.class_id == class_id)
    if name:
        query = query.filter(models.User.name.contains(name))
    if student_id:
        query = query.filter(models.User.student_id.contains(student_id))
    if status:
        query = query.filter(models.User.health_status == status)
    
    students = query.offset((page - 1) * size).limit(size).all()
    
    # 确保返回的对象包含前端需要的 class_name (带专业的)
    result = []
    for s in students:
        s_dict = {k: v for k, v in s.__dict__.items() if not k.startswith("_")}
        s_dict["class_name"] = s.class_name # 使用我们重构后的带专业的 class_name
        s_dict["major_name"] = s.major # 专业名称
        result.append(s_dict)
    return result


@router.get("/activities/invalid", response_model=List[schemas.InvalidActivityOut])
async def get_invalid_activities(
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    获取阳光跑异常记录：
    - is_valid = False 且 fail_reason 非空（人脸比对失败、配速异常、配速过快、里程不足等）
    仅返回当前教师所带班级内学生的数据（统一使用 get_managed_students_query）。
    """
    # 使用统一的教师管辖学生查询逻辑（与首页统计一致）
    student_query = await get_managed_students_query(current_user, db)
    managed_student_ids = [u.id for u in student_query.with_entities(models.User.id).all()]

    if not managed_student_ids:
        return []

    # 查询异常活动：仅阳光跑（含旧库 source 为空），不含任务跑
    activities = (
        db.query(models.Activity)
        .join(models.User, models.Activity.user_id == models.User.id)
        .outerjoin(models.ActivityMetrics, models.Activity.id == models.ActivityMetrics.activity_id)
        .filter(
            models.Activity.is_valid.is_(False),
            models.Activity.fail_reason.isnot(None),
            models.Activity.fail_reason != "",
            models.Activity.user_id.in_(managed_student_ids),
        )
        .filter(sunshine_run_filter())
        .order_by(models.Activity.started_at.desc())
        .all()
    )

    results: List[schemas.InvalidActivityOut] = []

    for activity in activities:
        user = activity.user
        cls = getattr(user, "student_class", None)
        metrics = activity.metrics

        # 提取起跑 / 终点照片（按 evidence.id 顺序取前两个 camera 证据）
        start_photo_url = None
        end_photo_url = None
        sorted_evidence = sorted(activity.evidence, key=lambda e: e.id or 0)
        for ev in sorted_evidence:
            if ev.evidence_type == "camera":
                if not start_photo_url:
                    start_photo_url = ev.data_ref
                elif not end_photo_url:
                    end_photo_url = ev.data_ref
                    break

        results.append(
            schemas.InvalidActivityOut(
                id=activity.id,
                student_name=user.name if user else "未知学生",
                student_id=user.student_id if user else None,
                class_name=user.class_name,
                fail_reason=activity.fail_reason,
                distance=metrics.distance if metrics else None,
                duration=metrics.duration if metrics else None,
                pace=metrics.pace if metrics else None,
                started_at=activity.started_at,
                start_photo_url=start_photo_url,
                end_photo_url=end_photo_url,
            )
        )

    return results


@router.post("/activities/{activity_id}/resolve")
async def resolve_activity_exception(
    activity_id: int,
    payload: schemas.ResolveActivityExceptionRequest,
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db),
):
    """
    教师人工处理阳光跑异常：
    - confirm_cheat：确认作弊，保留无效状态
    - restore_valid：恢复为有效记录
    权限：统一管辖逻辑。
    """
    student_query = await get_managed_students_query(current_user, db)
    managed_student_ids = [u.id for u in student_query.with_entities(models.User.id).all()]
    
    activity = (
        db.query(models.Activity)
        .filter(
            models.Activity.id == activity_id,
            models.Activity.user_id.in_(managed_student_ids),
        )
        .first()
    )

    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在或无权限访问")

    action = payload.action
    if action not in ("confirm_cheat", "restore_valid"):
        raise HTTPException(status_code=400, detail="不支持的操作类型")

    if action == "confirm_cheat":
        activity.is_valid = False
        if not activity.fail_reason:
            activity.fail_reason = "教师确认作弊"
    else:
        activity.is_valid = True
        activity.fail_reason = None
        activity.face_verified = True

    db.commit()
    db.refresh(activity)
    return {"message": "处理成功", "activity_id": activity.id, "action": action}


@router.get("/export/running-grades")
async def export_running_grades(
    class_id: int,
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db),
):
    """
    导出指定班级的阳光跑成绩汇总（CSV，可用 Excel 打开）。
    计分规则与学生端 sunshine-detail.vue 完全一致。
    权限：统一管辖逻辑。
    """
    student_query = await get_managed_students_query(current_user, db)
    
    # 查询班级内属于当前教师管辖的学生
    students = student_query.filter(
        models.User.class_id == class_id,
    ).all()
    
    cls = db.query(models.Class).filter(models.Class.id == class_id).first()
    cls_name = cls.name if cls else f"Class_{class_id}"

    # 生成 CSV 内容
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["姓名", "学号", "班级", "有效阳光跑次数", "阳光跑得分"])

    for student in students:
        valid_count = (
            db.query(func.count(models.Activity.id))
            .filter(
                models.Activity.user_id == student.id,
                models.Activity.is_valid.is_(True),
            )
            .filter(sunshine_run_filter())
            .scalar()
        )
        score = calculate_total_score(valid_count or 0)
        writer.writerow([student.name, student.student_id or "", cls_name, valid_count or 0, score])

    output.seek(0)
    filename = f"running_grades_{cls_name}.csv"
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Content-Type": "text/csv; charset=utf-8",
    }
    return StreamingResponse(output, headers=headers)


@router.post("/tasks", response_model=schemas.TaskOut)
async def create_teacher_task(
    task_in: schemas.TaskCreate,
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db),
):
    """教师发布任务（与学生端「我的任务」、任务跑步关联）"""
    if task_in.starts_at and task_in.deadline and task_in.starts_at > task_in.deadline:
        raise HTTPException(status_code=400, detail="任务开始时间不能晚于截止时间")
    t = models.Task(
        title=task_in.title,
        type=task_in.type,
        min_distance=task_in.min_distance,
        min_duration=task_in.min_duration,
        min_count=task_in.min_count,
        starts_at=task_in.starts_at,
        deadline=task_in.deadline,
        description=task_in.description,
        target_group=task_in.target_group or "all",
        class_id=task_in.class_id,
        video_url=task_in.video_url,
        created_by=current_user.id,
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


@router.delete("/tasks/{task_id}")
async def delete_teacher_task(
    task_id: int,
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db),
):
    task = (
        db.query(models.Task)
        .filter(models.Task.id == task_id, models.Task.created_by == current_user.id)
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    sub = db.query(models.Activity).filter(models.Activity.task_id == task_id).count()
    if sub > 0:
        raise HTTPException(status_code=400, detail="已有学生任务运动记录，无法删除")
    db.delete(task)
    db.commit()
    return {"success": True}


@router.get("/tasks")
async def get_teacher_tasks(
    status: str = "active",
    page: int = 1,
    size: int = 20,
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    """获取该教师发布的任务及其统计（统一管理逻辑）"""
    student_query = await get_managed_students_query(current_user, db)
    managed_student_ids = [u.id for u in student_query.with_entities(models.User.id).all()]
    managed_student_count = len(managed_student_ids)

    query = db.query(models.Task).filter(models.Task.created_by == current_user.id)
    now = datetime.utcnow()
    if status == "active":
        query = query.filter(or_(models.Task.deadline == None, models.Task.deadline > now))
    elif status == "ended":
        query = query.filter(models.Task.deadline <= now)
        
    total = query.count()
    tasks = query.offset((page - 1) * size).limit(size).all()
    
    result = []
    for task in tasks:
        completed_count = 0
        if managed_student_ids:
            completed_count = (
                db.query(func.count(func.distinct(models.Activity.user_id)))
                .filter(
                    models.Activity.task_id == task.id,
                    models.Activity.source == "task",
                    models.Activity.type == task.type,
                    models.Activity.is_valid.is_(True),
                    models.Activity.user_id.in_(managed_student_ids),
                )
                .scalar()
                or 0
            )

        result.append({
            "id": task.id,
            "title": task.title,
            "type": task.type,
            "description": task.description,
            "starts_at": task.starts_at,
            "deadline": task.deadline,
            "total_students": managed_student_count,
            "completed_count": completed_count,
            "status": "ongoing" if not task.deadline or task.deadline > now else "ended"
        })
    return {"items": result, "total": total}

@router.get("/tasks/{task_id}")
async def get_task_detail(
    task_id: int,
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db),
):
    """任务详情：仅统计「任务跑步/任务体测」提交记录（与阳光跑区分）"""
    task = (
        db.query(models.Task)
        .filter(models.Task.id == task_id, models.Task.created_by == current_user.id)
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    student_query = await get_managed_students_query(current_user, db)
    if task.class_id is not None:
        student_query = student_query.filter(models.User.class_id == task.class_id)
    students = student_query.all()

    student_statuses = []
    for s in students:
        act = (
            db.query(models.Activity)
            .filter(
                models.Activity.user_id == s.id,
                models.Activity.task_id == task.id,
                models.Activity.source == "task",
                models.Activity.type == task.type,
            )
            .order_by(models.Activity.started_at.desc())
            .first()
        )
        done = act is not None and act.is_valid
        metric_value = "-"
        teacher_score = None
        activity_id = None
        if act:
            activity_id = act.id
            if act.metrics:
                if task.type == "run":
                    metric_value = f"{act.metrics.distance or 0:.2f}km · {act.metrics.duration or 0}秒"
                else:
                    metric_value = f"{act.metrics.count or 0}次"
                if act.metrics.teacher_score is not None:
                    teacher_score = act.metrics.teacher_score

        student_statuses.append(
            {
                "student_id": s.id,
                "student_no": s.student_id,
                "student_name": s.name,
                "status": "completed" if done else "uncompleted",
                "activity_id": activity_id,
                "teacher_score": teacher_score,
                "metric_value": metric_value,
                "avatar_url": getattr(s, "avatar_url", None) or "",
            }
        )

    total_count = len(student_statuses)
    completed_count = sum(1 for x in student_statuses if x["status"] == "completed")

    return {
        "id": task.id,
        "title": task.title,
        "type": task.type,
        "description": task.description,
        "starts_at": task.starts_at,
        "deadline": task.deadline,
        "min_distance": task.min_distance,
        "min_duration": task.min_duration,
        "min_count": task.min_count,
        "video_url": task.video_url,
        "total_students": total_count,
        "completed_count": completed_count,
        "student_statuses": student_statuses,
    }


@router.get("/task-runs/{activity_id}")
async def get_teacher_task_run_detail(
    activity_id: int,
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db),
):
    """教师查看某条任务运动记录（地图轨迹 + 指标），与阳光跑无关"""
    student_query = await get_managed_students_query(current_user, db)
    managed_ids = [u.id for u in student_query.with_entities(models.User.id).all()]

    act = (
        db.query(models.Activity)
        .filter(
            models.Activity.id == activity_id,
            models.Activity.source == "task",
            models.Activity.task_id.isnot(None),
        )
        .first()
    )
    if not act or act.user_id not in managed_ids:
        raise HTTPException(status_code=404, detail="记录不存在或无权限")

    stu = db.query(models.User).filter(models.User.id == act.user_id).first()
    t = db.query(models.Task).filter(models.Task.id == act.task_id).first()
    metrics = db.query(models.ActivityMetrics).filter(models.ActivityMetrics.activity_id == act.id).first()

    metrics_out = None
    if metrics:
        metrics_out = {
            "id": metrics.id,
            "activity_id": metrics.activity_id,
            "distance": metrics.distance,
            "duration": metrics.duration,
            "pace": metrics.pace,
            "trajectory": metrics.trajectory,
            "checkpoints": metrics.checkpoints,
            "count": metrics.count,
            "step_count": metrics.step_count,
            "qualified": metrics.qualified,
            "video_url": metrics.video_url,
            "score": metrics.score,
            "score_detail": metrics.score_detail,
            "teacher_score": metrics.teacher_score,
            "teacher_comment": metrics.teacher_comment,
            "scored_at": metrics.scored_at,
            "scored_by": metrics.scored_by,
        }

    return {
        "activity": {
            "id": act.id,
            "type": act.type,
            "source": act.source,
            "task_id": act.task_id,
            "task_title": t.title if t else "",
            "started_at": act.started_at,
            "ended_at": act.ended_at,
            "is_valid": act.is_valid,
            "fail_reason": act.fail_reason,
            "status": act.status,
        },
        "student": {
            "id": stu.id if stu else act.user_id,
            "name": stu.name if stu else "",
            "student_no": stu.student_id if stu else None,
            "avatar_url": getattr(stu, "avatar_url", None) if stu else None,
        },
        "metrics": metrics_out,
    }

@router.put("/health/requests/{req_id}/review")
async def review_health_request(
    req_id: int,
    payload: dict = Body(...),
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    """审批请假/伤病申请"""
    hr = db.query(models.HealthRequest).filter(models.HealthRequest.id == req_id).first()
    if not hr:
        raise HTTPException(status_code=404, detail="申请记录不存在")
        
    status = payload.get("status")
    if status not in ["approved", "rejected"]:
        raise HTTPException(status_code=400, detail="审批状态不合法")
        
    hr.status = status
    # 如果批准，同时更新学生的健康状态
    if status == "approved":
        student = db.query(models.User).filter(models.User.id == hr.student_id).first()
        if student:
            # 映射类型：如果申请类型是 'injury'，状态设为 'injured'；其他非 normal 统一映射
            raw_type = hr.type
            if raw_type == "injury":
                new_status = "injured"
            elif raw_type in ["leave", "sick"]:
                new_status = "leave"
            else:
                new_status = "abnormal"
            
            student.health_status = new_status
            student.abnormal_reason = hr.reason
    elif status == "rejected":
        # 如果是驳回，可以根据需要保留或清除状态，这里通常保持原样
        hr.updated_at = datetime.utcnow()
    db.commit()
    return {"ok": True}

@router.put("/students/{student_id}", response_model=schemas.StudentDetail)
async def update_student(
    student_id: int,
    student_in: schemas.StudentUpdate,
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    student_query = await get_managed_students_query(current_user, db)
    student = student_query.filter(models.User.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found or no permission")
        
    if student_in.student_id is not None:
        student.student_id = student_in.student_id
    if student_in.health_status is not None:
        student.health_status = student_in.health_status
    if student_in.abnormal_reason is not None:
        student.abnormal_reason = student_in.abnormal_reason
    if student_in.group_name is not None:
        student.group_name = student_in.group_name
    if student_in.class_id is not None:
        student.class_id = student_in.class_id
        
    db.commit()
    db.refresh(student)
    return student

@router.post("/students/bulk-update")
async def bulk_update_students(
    update_in: schemas.BulkUpdateStudent,
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    student_query = await get_managed_students_query(current_user, db)
    query = student_query.filter(
        models.User.id.in_(update_in.student_ids)
    )
    
    update_data = {}
    if update_in.health_status is not None:
        update_data[models.User.health_status] = update_in.health_status
    if update_in.abnormal_reason is not None:
        update_data[models.User.abnormal_reason] = update_in.abnormal_reason
    if update_in.group_name is not None:
        update_data[models.User.group_name] = update_in.group_name
    if update_in.class_id is not None:
        update_data[models.User.class_id] = update_in.class_id
        
    if not update_data:
        raise HTTPException(status_code=400, detail="No update data provided")
        
    rows_updated = query.update(update_data, synchronize_session=False)
    db.commit()
    return {"message": "Success", "updated_count": rows_updated}

@router.post("/students/export")
async def export_students(
    export_in: schemas.BulkUpdateStudent,
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    import csv
    import io
    from fastapi.responses import StreamingResponse

    student_query = await get_managed_students_query(current_user, db)
    query = student_query
    
    if export_in.student_ids:
        query = query.filter(models.User.id.in_(export_in.student_ids))
    else:
        if export_in.class_id:
            query = query.filter(models.User.class_id == export_in.class_id)
        if export_in.health_status:
            query = query.filter(models.User.health_status == export_in.health_status)
        if export_in.group_name:
            query = query.filter(models.User.group_name == export_in.group_name)
        
    students = query.all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Name', 'Student ID', 'Phone', 'Class ID', 'Group', 'Health Status', 'Abnormal Reason'])
    
    for s in students:
        writer.writerow([
            s.id, s.name, s.student_id or '', s.phone,
        s.class_id or '', s.group_name or '', s.health_status, s.abnormal_reason or ''
        ])
        
    output.seek(0)
    response = StreamingResponse(iter([output.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=students_export.csv"
    return response

# 第三阶段新增：教师打分API
@router.post("/activities/{activity_id}/score")
async def score_activity(
    activity_id: int,
    score_data: schemas.TeacherScoreCreate,
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    """教师对学生活动进行打分 (统一管理)"""
    student_query = await get_managed_students_query(current_user, db)
    managed_student_ids = [u.id for u in student_query.with_entities(models.User.id).all()]
    
    activity = db.query(models.Activity).filter(
        models.Activity.id == activity_id,
        models.Activity.user_id.in_(managed_student_ids)
    ).first()
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在或无权限")
    
    metrics = db.query(models.ActivityMetrics).filter(
        models.ActivityMetrics.activity_id == activity_id
    ).first()
    
    if not metrics:
        raise HTTPException(status_code=404, detail="活动指标不存在")
    
    metrics.teacher_score = score_data.score
    metrics.teacher_comment = score_data.comment
    metrics.scored_at = datetime.utcnow()
    metrics.scored_by = current_user.id
    
    student = db.query(models.User).filter(models.User.id == activity.user_id).first()
    if student:
        all_scored_activities = db.query(models.ActivityMetrics).join(
            models.Activity
        ).filter(
            models.Activity.user_id == student.id,
            models.ActivityMetrics.teacher_score.isnot(None)
        ).all()
        
        if all_scored_activities:
            total_score = sum(m.teacher_score for m in all_scored_activities)
            student.regular_score = round(total_score / len(all_scored_activities), 2)
    
    db.commit()
    db.refresh(metrics)
    return {"message": "打分成功", "activity_id": activity_id, "score": metrics.teacher_score}

@router.get("/tasks/{task_id}/scores")
async def get_task_scores(
    task_id: int,
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    task = db.query(models.Task).filter(models.Task.id == task_id, models.Task.created_by == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    student_query = await get_managed_students_query(current_user, db)
    if task.class_id:
        student_query = student_query.filter(models.User.class_id == task.class_id)
    students = student_query.all()
    
    scores = []
    for student in students:
        activities = db.query(models.Activity).filter(
            models.Activity.user_id == student.id,
            models.Activity.type == task.type
        ).all()
        for activity in activities:
            metrics = db.query(models.ActivityMetrics).filter(
                models.ActivityMetrics.activity_id == activity.id
            ).first()
            if metrics and metrics.teacher_score is not None:
                scores.append({
                    "activity_id": activity.id,
                    "student_id": student.id,
                    "student_name": student.name,
                    "score": metrics.teacher_score,
                    "comment": metrics.teacher_comment,
                    "scored_at": metrics.scored_at
                })
    return {"scores": scores}

@router.get("/stats/task-completion")
async def get_task_completion_stats(
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    tasks = db.query(models.Task).filter(models.Task.created_by == current_user.id).all()
    student_query = await get_managed_students_query(current_user, db)
    stats = []
    managed_student_ids = [u.id for u in student_query.with_entities(models.User.id).all()]
    
    for task in tasks:
        t_query = student_query
        if task.class_id:
            t_query = t_query.filter(models.User.class_id == task.class_id)
        
        task_students = t_query.all()
        total_students = len(task_students)
        t_student_ids = [s.id for s in task_students]
        
        completed_count = 0
        if t_student_ids:
            # Fix: Count unique students who have at least one qualified activity for this task
            completed_count = db.query(func.count(func.distinct(models.Activity.user_id))).join(models.ActivityMetrics).filter(
                models.Activity.user_id.in_(t_student_ids),
                models.Activity.type == task.type,
                models.ActivityMetrics.qualified == True
            ).scalar() or 0
            
        stats.append({
            "task_id": task.id,
            "task_title": task.title,
            "total_students": total_students,
            "completed_count": completed_count,
            "completion_rate": round((completed_count / total_students * 100), 2) if total_students > 0 else 0
        })
    return {"tasks": stats}

@router.get("/activities/abnormal/v2")
async def get_abnormal_activities_v2(
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    """获取异常运动数据 (统一管理)"""
    student_query = await get_managed_students_query(current_user, db)
    managed_student_ids = [u.id for u in student_query.with_entities(models.User.id).all()]
    
    if not managed_student_ids:
        return []

    activities = (
        db.query(models.Activity)
        .filter(
            models.Activity.is_valid == False,
            models.Activity.fail_reason != None,
            models.Activity.user_id.in_(managed_student_ids),
        )
        .filter(sunshine_run_filter())
        .order_by(models.Activity.started_at.desc())
        .limit(50)
        .all()
    )
    
    return [
        {
            "id": act.id,
            "student_name": act.user.name if act.user else "未知",
            "reason": act.fail_reason,
            "type": act.type,
            "time": act.started_at
        } for act in activities
    ]

@router.post("/students/{student_id}/notify")
async def notify_student(
    student_id: int,
    payload: schemas.StudentNotify,
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    return {"message": "通知已发送", "student_id": student_id, "content": payload.message}
