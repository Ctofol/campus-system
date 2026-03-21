from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List
import io
import csv
from datetime import datetime, timedelta
from .. import models, schemas, auth
from ..services.score_service import calculate_total_score
from ..database import get_db

router = APIRouter(prefix="/teacher", tags=["teacher"])

@router.get("/stats", response_model=schemas.TeacherStatsOut)
async def get_teacher_stats(
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    """Get teacher dashboard statistics - only for students in teacher's bound classes"""
    # 基于 TeacherClass 绑定关系获取教师可管理的班级名称
    tc_rows = db.query(models.TeacherClass).filter(
        models.TeacherClass.teacher_id == current_user.id
    ).all()
    class_names = [r.class_name for r in tc_rows]

    if class_names:
        teacher_class_ids = [
            c.id
            for c in db.query(models.Class)
            .filter(models.Class.name.in_(class_names))
            .all()
        ]
    else:
        teacher_class_ids = []

    # 1. Student Count (only in teacher's classes)
    if teacher_class_ids:
        student_count = db.query(models.User).filter(
            models.User.role == "student",
            models.User.class_id.in_(teacher_class_ids)
        ).count()
    else:
        student_count = 0
    
    # 2. Pending Approvals (Health Requests from teacher's students)
    if teacher_class_ids:
        pending_approvals = db.query(models.HealthRequest).join(
            models.User, models.HealthRequest.student_id == models.User.id
        ).filter(
            models.HealthRequest.status == "pending",
            models.User.class_id.in_(teacher_class_ids)
        ).count()
    else:
        pending_approvals = 0
    
    # 3. Abnormal Count (students with non-normal health status in teacher's classes)
    if teacher_class_ids:
        abnormal_count = db.query(models.User).filter(
            models.User.role == "student",
            models.User.class_id.in_(teacher_class_ids),
            models.User.health_status != "normal"
        ).count()
    else:
        abnormal_count = 0
    
    # 4. Today Check-in (Activities today from teacher's students)
    today = datetime.utcnow().date()
    today_start = datetime(today.year, today.month, today.day)
    
    if teacher_class_ids:
        today_checkin = db.query(models.Activity).join(
            models.User, models.Activity.user_id == models.User.id
        ).filter(
            models.Activity.started_at >= today_start,
            models.User.class_id.in_(teacher_class_ids)
        ).count()
    else:
        today_checkin = 0
    
    # 5. Task Count (active tasks created by this teacher - not expired)
    now = datetime.utcnow()
    task_count = db.query(models.Task).filter(
        models.Task.created_by == current_user.id,
        or_(models.Task.deadline == None, models.Task.deadline > now)  # 未设置截止时间或未过期
    ).count()
    
    # 6. Average Pace (calculate from recent running activities of teacher's students)
    if teacher_class_ids:
        recent_runs = db.query(models.ActivityMetrics).join(
            models.Activity
        ).join(
            models.User, models.Activity.user_id == models.User.id
        ).filter(
            models.Activity.type == "run",
            models.User.class_id.in_(teacher_class_ids),
            models.ActivityMetrics.distance > 0,
            models.ActivityMetrics.duration > 0
        ).limit(100).all()
        
        if recent_runs:
            total_pace_seconds = sum(
                int(m.duration / m.distance / 60) for m in recent_runs if m.distance > 0
            )
            avg_pace_seconds = total_pace_seconds // len(recent_runs)
            avg_pace = f"{avg_pace_seconds // 60}'{avg_pace_seconds % 60}\""
        else:
            avg_pace = "--"
    else:
        avg_pace = "--"
    
    # 7. Compliance Rate (students with activities in last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    
    if teacher_class_ids and student_count > 0:
        active_students = db.query(models.Activity.user_id).join(
            models.User, models.Activity.user_id == models.User.id
        ).filter(
            models.Activity.started_at >= week_ago,
            models.User.class_id.in_(teacher_class_ids)
        ).distinct().count()
        compliance_rate = int((active_students / student_count * 100))
    else:
        compliance_rate = 0
    
    # 8. Qualified Rate (达标率 - 近7天内达标学生占比)
    qualified_rate = 0
    if teacher_class_ids and student_count > 0:
        try:
            # 获取近7天内有达标活动的学生数
            qualified_students = db.query(models.Activity.user_id).join(
                models.User, models.Activity.user_id == models.User.id
            ).join(
                models.ActivityMetrics, models.Activity.id == models.ActivityMetrics.activity_id
            ).filter(
                models.Activity.started_at >= week_ago,
                models.User.class_id.in_(teacher_class_ids),
                models.ActivityMetrics.qualified.is_(True)
            ).distinct().count()
            qualified_rate = int((qualified_students / student_count * 100))
        except Exception as e:
            print(f"Error calculating qualified_rate: {e}")
            qualified_rate = 0
    
    # 9. Completion Rate (完成率 - 本周任务完成占比)
    completion_rate = 0
    # 获取本周开始时间
    today_dt = datetime.utcnow()
    week_start = today_dt - timedelta(days=today_dt.weekday())
    week_start = datetime(week_start.year, week_start.month, week_start.day)
    
    if teacher_class_ids and student_count > 0:
        try:
            # 获取本周该教师发布的任务
            weekly_tasks = db.query(models.Task).filter(
                models.Task.created_by == current_user.id,
                models.Task.deadline >= week_start
            ).all()
            
            if weekly_tasks:
                total_assignments = 0
                total_completions = 0
                
                for task in weekly_tasks:
                    # 获取该任务关联的学生数（根据target_group和class_id）
                    if task.target_group == "all":
                        task_students = db.query(models.User).filter(
                            models.User.class_id == task.class_id,
                            models.User.role == "student"
                        ).all()
                    else:
                        task_students = db.query(models.User).filter(
                            models.User.class_id == task.class_id,
                            models.User.role == "student",
                            models.User.group_name == task.target_group
                        ).all()
                    
                    task_student_ids = [s.id for s in task_students]
                    total_assignments += len(task_student_ids)
                    
                    # 统计完成该任务的学生数
                    if len(task_student_ids) > 0:
                        if task.type == "run":
                            completed = db.query(models.Activity.user_id).join(
                                models.ActivityMetrics
                            ).filter(
                                models.Activity.user_id.in_(task_student_ids),
                                models.Activity.type == "run",
                                models.Activity.started_at >= week_start,
                                models.ActivityMetrics.distance >= (task.min_distance or 0),
                                models.ActivityMetrics.duration >= (task.min_duration or 0) * 60
                            ).distinct().count()
                        else:
                            completed = db.query(models.Activity.user_id).join(
                                models.ActivityMetrics
                            ).filter(
                                models.Activity.user_id.in_(task_student_ids),
                                models.Activity.type == "test",
                                models.Activity.started_at >= week_start,
                                models.ActivityMetrics.count >= (task.min_count or 0)
                            ).distinct().count()
                        
                        total_completions += completed
                
                completion_rate = int((total_completions / total_assignments * 100)) if total_assignments > 0 else 0
        except Exception as e:
            print(f"Error calculating completion_rate: {e}")
            completion_rate = 0
    
    return {
        "student_count": student_count,
        "today_checkin": today_checkin,
        "abnormal_count": abnormal_count,
        "pending_approvals": pending_approvals,
        "pending_health": pending_approvals,
        "pending_activities": 0,
        "avg_pace": avg_pace,
        "task_count": task_count,
        "compliance_rate": compliance_rate,
        "qualified_rate": qualified_rate,
        "completion_rate": completion_rate
    }

@router.get("/weekly-trend")
async def get_weekly_trend(
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    """Get weekly activity trend data - only for students in teacher's bound classes"""
    days = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    trend_data = []
    
    # Get teacher's bound class IDs via TeacherClass
    tc_rows = db.query(models.TeacherClass).filter(
        models.TeacherClass.teacher_id == current_user.id
    ).all()
    class_names = [r.class_name for r in tc_rows]
    if class_names:
        teacher_class_ids = [
            c.id
            for c in db.query(models.Class)
            .filter(models.Class.name.in_(class_names))
            .all()
        ]
    else:
        teacher_class_ids = []
    
    if not teacher_class_ids:
        # No classes, return empty trend
        for i in range(6, -1, -1):
            date = datetime.utcnow() - timedelta(days=i)
            trend_data.append({
                "day": days[(date.weekday()) % 7],
                "val": 0,
                "color": "linear-gradient(180deg, #e0e0e0 0%, #f5f5f5 100%)",
                "count": 0
            })
        return trend_data
    
    # Get activities for the past 7 days from teacher's students
    for i in range(6, -1, -1):
        date = datetime.utcnow() - timedelta(days=i)
        day_start = datetime(date.year, date.month, date.day)
        day_end = day_start + timedelta(days=1)
        
        count = db.query(models.Activity).join(
            models.User, models.Activity.user_id == models.User.id
        ).filter(
            models.Activity.started_at >= day_start,
            models.Activity.started_at < day_end,
            models.User.class_id.in_(teacher_class_ids)
        ).count()
        
        # Calculate percentage (max 100)
        # Assume 50 activities per day is 100%
        percentage = min(int(count / 50 * 100), 100) if count > 0 else 0
        
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

@router.get("/class/{class_id}/analysis", response_model=schemas.ClassAnalysisOut)
async def get_class_analysis(
    class_id: int,
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    """Get class analysis data（权限：TeacherClass 绑定班级）"""
    tc_rows = db.query(models.TeacherClass).filter(
        models.TeacherClass.teacher_id == current_user.id
    ).all()
    class_names = [r.class_name for r in tc_rows]
    cls = None
    if class_names:
        cls = db.query(models.Class).filter(
            models.Class.id == class_id,
            models.Class.name.in_(class_names)
        ).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found or not authorized")
    
    # Get students in this class
    students = db.query(models.User).filter(
        models.User.class_id == class_id,
        models.User.role == "student"
    ).all()
    
    student_count = len(students)
    
    if student_count == 0:
        return {
            "class_id": class_id,
            "class_name": cls.name,
            "student_count": 0,
            "avg_distance": 0.0,
            "avg_duration": 0,
            "completion_rate": 0.0
        }
    
    # Calculate averages from activities
    student_ids = [s.id for s in students]
    
    # Get all activities for these students
    activities = db.query(models.Activity).filter(
        models.Activity.user_id.in_(student_ids)
    ).all()
    
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
        "class_name": cls.name,
        "student_count": student_count,
        "avg_distance": round(avg_distance, 2),
        "avg_duration": avg_duration,
        "completion_rate": round(completion_rate, 2)
    }

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
    """Get all students managed by the teacher (based on TeacherClass bindings)."""
    # Only show students in classes bound to the current teacher via TeacherClass
    tc_rows = db.query(models.TeacherClass).filter(
        models.TeacherClass.teacher_id == current_user.id
    ).all()
    class_names = [r.class_name for r in tc_rows]

    if not class_names:
        return []

    query = db.query(models.User).join(
        models.Class, models.User.class_id == models.Class.id
    ).filter(
        models.User.role == "student",
        models.Class.name.in_(class_names)
    )
    
    if class_id:
        query = query.filter(models.User.class_id == class_id)
    if name:
        query = query.filter(models.User.name.contains(name))
    if student_id:
        query = query.filter(models.User.student_id.contains(student_id))
    if status:
        query = query.filter(models.User.health_status == status)
    
    students = query.offset((page - 1) * size).limit(size).all()
    return students


@router.get("/activities/invalid", response_model=List[schemas.InvalidActivityOut])
async def get_invalid_activities(
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    获取阳光跑异常记录：
    - is_valid = False 且 fail_reason 非空（人脸比对失败、配速异常、配速过快、里程不足等）
    仅返回当前教师所带班级内学生的数据。
    """
    # 1. 获取教师绑定的班级（通过 TeacherClass）
    tc_rows = db.query(models.TeacherClass).filter(
        models.TeacherClass.teacher_id == current_user.id
    ).all()
    class_names = [r.class_name for r in tc_rows]

    if not class_names:
        return []

    # 2. 查询异常活动（仅跑步，任意无效原因都展示）
    activities = (
        db.query(models.Activity)
        .join(models.User, models.Activity.user_id == models.User.id)
        .join(models.Class, models.User.class_id == models.Class.id)
        .outerjoin(models.ActivityMetrics, models.Activity.id == models.ActivityMetrics.activity_id)
        .filter(
            models.Activity.type == "run",
            models.Activity.is_valid.is_(False),
            models.Activity.fail_reason.isnot(None),
            models.Activity.fail_reason != "",
            models.Class.name.in_(class_names),
        )
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
                class_name=cls.name if cls else None,
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
    权限：仅能处理 TeacherClass 绑定班级内学生的活动。
    """
    # 通过 TeacherClass 获取当前教师管理的班级 ID
    tc_rows = db.query(models.TeacherClass).filter(
        models.TeacherClass.teacher_id == current_user.id
    ).all()
    class_names = [r.class_name for r in tc_rows]
    if not class_names:
        raise HTTPException(status_code=403, detail="当前教师没有管理的班级")
    teacher_class_ids = [
        c.id for c in db.query(models.Class).filter(models.Class.name.in_(class_names)).all()
    ]
    if not teacher_class_ids:
        raise HTTPException(status_code=403, detail="当前教师没有管理的班级")

    activity = (
        db.query(models.Activity)
        .join(models.User, models.Activity.user_id == models.User.id)
        .filter(
            models.Activity.id == activity_id,
            models.User.class_id.in_(teacher_class_ids),
        )
        .first()
    )

    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在或无权限访问")

    action = payload.action
    if action not in ("confirm_cheat", "restore_valid"):
        raise HTTPException(status_code=400, detail="不支持的操作类型")

    if action == "confirm_cheat":
        # 确认作弊：保持无效状态，并标记原因
        activity.is_valid = False
        if not activity.fail_reason:
            activity.fail_reason = "教师确认作弊"
    else:
        # 恢复有效：标记为有效，并清空失败原因
        activity.is_valid = True
        activity.fail_reason = None
        # 人脸校验通过（人工确认）
        activity.face_verified = True

    db.commit()
    db.refresh(activity)

    # 累计有效次数依赖 get_sunshine_stats 的动态统计，
    # 这里不单独存储计数，只需保持 activities 表中的 is_valid 状态正确。
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
    权限：仅可导出 TeacherClass 绑定班级。
    """
    tc_rows = db.query(models.TeacherClass).filter(
        models.TeacherClass.teacher_id == current_user.id
    ).all()
    class_names = [r.class_name for r in tc_rows]
    cls = None
    if class_names:
        cls = db.query(models.Class).filter(
            models.Class.id == class_id,
            models.Class.name.in_(class_names)
        ).first()
    if not cls:
        raise HTTPException(status_code=404, detail="班级不存在或无权限访问")

    # 查询班级学生
    students = (
        db.query(models.User)
        .filter(
            models.User.class_id == class_id,
            models.User.role == "student",
        )
        .all()
    )

    # 生成 CSV 内容
    output = io.StringIO()
    writer = csv.writer(output)
    # 表头
    writer.writerow(["姓名", "学号", "班级", "有效阳光跑次数", "阳光跑得分"])

    for student in students:
        # 统计该生有效阳光跑次数
        valid_count = (
            db.query(func.count(models.Activity.id))
            .filter(
                models.Activity.user_id == student.id,
                models.Activity.type == "run",
                models.Activity.is_valid.is_(True),
            )
            .scalar()
        )
        score = calculate_total_score(valid_count or 0)

        writer.writerow(
            [
                student.name,
                student.student_id or "",
                cls.name,
                valid_count or 0,
                score,
            ]
        )

    output.seek(0)
    filename = f"running_grades_class_{class_id}.csv"
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Content-Type": "text/csv; charset=utf-8",
    }

    return StreamingResponse(output, headers=headers)
