from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from datetime import datetime, timedelta
from .. import models, config

async def get_managed_students_query(current_user: models.User, db: Session):
    """获取教师管辖的学生查询对象（统一逻辑：支持选科、班级管理、直接关联）"""
    # 1. 获取教师选科
    ts_rows = db.query(models.TeacherSubject).filter(
        models.TeacherSubject.teacher_id == current_user.id
    ).all()
    subjects = [r.subject_name for r in ts_rows]
    
    # 2. 获取教师直接管辖的班级 (Class.teacher_id)
    direct_class_ids = [c.id for c in db.query(models.Class).filter(models.Class.teacher_id == current_user.id).all()]
    
    # 3. 获取教师绑定的班级名称 (TeacherClass.class_name)
    tc_rows = db.query(models.TeacherClass).filter(
        models.TeacherClass.teacher_id == current_user.id
    ).all()
    class_names = [r.class_name for r in tc_rows]
    
    # 构建过滤条件
    conditions = []
    if subjects:
        conditions.append(models.User.subject.in_(subjects))
    if direct_class_ids:
        conditions.append(models.User.class_id.in_(direct_class_ids))
    if class_names:
        # 子查询：匹配班级名称所在的班级 ID
        bound_class_ids = [c.id for c in db.query(models.Class).filter(models.Class.name.in_(class_names)).all()]
        if bound_class_ids:
            conditions.append(models.User.class_id.in_(bound_class_ids))
            
    base_query = db.query(models.User).filter(models.User.role == "student")
    
    if not conditions:
        # 如果没有任何管理关系，则返回空结果查询
        return base_query.filter(models.User.id == -1)
        
    return base_query.filter(or_(*conditions))

async def get_teacher_stats_data(current_user: models.User, db: Session):
    """教师端统计逻辑：获取管辖范围内的学生统计数据"""
    student_query = await get_managed_students_query(current_user, db)
    managed_student_ids = [u.id for u in student_query.with_entities(models.User.id).all()]
    
    default_stats = {
        "student_count": 0, "today_checkin": 0, "abnormal_count": 0,
        "pending_approvals": 0, "pending_health": 0, "pending_activities": 0,
        "avg_pace": "--", "task_count": 0, "compliance_rate": 0,
        "qualified_rate": 0, "completion_rate": 0
    }
    
    if not managed_student_ids:
        return default_stats

    # 学生总数
    student_count = len(managed_student_ids)
    
    # 待审批请假 (Health Requests)
    pending_health = db.query(models.HealthRequest).filter(
        models.HealthRequest.status == "pending",
        models.HealthRequest.student_id.in_(managed_student_ids)
    ).count()
    
    # 待审批记录 (Activity Exceptions) - 仅统计阳光跑类型
    pending_activities = db.query(models.Activity).filter(
        models.Activity.type == "run",
        models.Activity.is_valid.is_(False),
        models.Activity.fail_reason.isnot(None),
        models.Activity.fail_reason != "",
        models.Activity.user_id.in_(managed_student_ids)
    ).count()
    
    # 身体状态异常人数
    abnormal_count = student_query.filter(models.User.health_status != "normal").count()
    
    # 今日打卡人数
    today = datetime.utcnow().date()
    today_start = datetime(today.year, today.month, today.day)
    today_checkin = db.query(models.Activity).filter(
        models.Activity.started_at >= today_start,
        models.Activity.user_id.in_(managed_student_ids)
    ).count()
    
    # 进行中任务数
    now = datetime.utcnow()
    task_count = db.query(models.Task).filter(
        models.Task.created_by == current_user.id,
        or_(models.Task.deadline == None, models.Task.deadline > now)
    ).count()
    
    # 平均配速 (近7天)
    week_ago = datetime.utcnow() - timedelta(days=7)
    activities = db.query(models.ActivityMetrics).join(
        models.Activity
    ).filter(
        models.Activity.type == "run",
        models.Activity.user_id.in_(managed_student_ids),
        models.Activity.started_at >= week_ago
    ).all()
    
    avg_pace = "--"
    if activities:
        total_dur = sum([a.duration for a in activities])
        avg_dur = int(total_dur / len(activities))
        avg_pace = f"{avg_dur // 60}'{avg_dur % 60:02d}\""
        
    # 达标率
    qualified_rate = 0
    if student_count > 0:
        qualified_students = db.query(models.Activity.user_id).join(
            models.ActivityMetrics, models.Activity.id == models.ActivityMetrics.activity_id
        ).filter(
            models.Activity.started_at >= week_ago,
            models.Activity.user_id.in_(managed_student_ids),
            models.ActivityMetrics.qualified.is_(True)
        ).distinct().count()
        qualified_rate = int((qualified_students / student_count * 100))

    # 任务完成率
    completion_rate = 0
    week_start = datetime(today.year, today.month, today.day) - timedelta(days=today.weekday())
    
    if student_count > 0:
        try:
            weekly_tasks = db.query(models.Task).filter(
                models.Task.created_by == current_user.id,
                models.Task.deadline >= week_start
            ).all()
            
            if weekly_tasks:
                total_assignments = 0
                total_completions = 0
                for task in weekly_tasks:
                    total_assignments += student_count
                    completed = db.query(models.Activity.user_id).join(
                        models.ActivityMetrics
                    ).filter(
                        models.Activity.user_id.in_(managed_student_ids),
                        models.Activity.started_at >= week_start,
                        models.Activity.is_valid.is_(True)
                    ).distinct().count()
                    total_completions += completed
                completion_rate = int((total_completions / total_assignments * 100)) if total_assignments > 0 else 0
        except Exception:
            completion_rate = 0

    return {
        "student_count": student_count,
        "today_checkin": today_checkin,
        "abnormal_count": abnormal_count,
        "pending_approvals": pending_health + pending_activities,
        "pending_health": pending_health,
        "pending_activities": pending_activities,
        "avg_pace": avg_pace,
        "task_count": task_count,
        "compliance_rate": qualified_rate,
        "qualified_rate": qualified_rate,
        "completion_rate": completion_rate
    }
