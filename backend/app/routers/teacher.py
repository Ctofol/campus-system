from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List
from datetime import datetime, timedelta
from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/teacher", tags=["teacher"])

@router.get("/stats", response_model=schemas.TeacherStatsOut)
async def get_teacher_stats(
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    """Get teacher dashboard statistics - only for students in teacher's classes"""
    
    # Get teacher's class IDs
    teacher_classes = db.query(models.Class).filter(
        models.Class.teacher_id == current_user.id
    ).all()
    teacher_class_ids = [c.id for c in teacher_classes]
    
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
    """Get weekly activity trend data - only for students in teacher's classes"""
    days = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    trend_data = []
    
    # Get teacher's class IDs
    teacher_classes = db.query(models.Class).filter(
        models.Class.teacher_id == current_user.id
    ).all()
    teacher_class_ids = [c.id for c in teacher_classes]
    
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
    """Get class analysis data"""
    # Verify teacher owns this class
    cls = db.query(models.Class).filter(
        models.Class.id == class_id,
        models.Class.teacher_id == current_user.id
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
    """Get all students managed by the teacher"""
    # Only show students in classes managed by the current teacher
    query = db.query(models.User).join(
        models.Class, models.User.class_id == models.Class.id
    ).filter(
        models.User.role == "student",
        models.Class.teacher_id == current_user.id
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
