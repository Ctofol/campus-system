from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from . import models, schemas, auth, database

# 初始化数据库表
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Campus Sports Health MVP")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
get_db = database.get_db

# --- Auth Interfaces ---

@app.post("/auth/register", response_model=schemas.Token)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.phone == user.phone).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Phone already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(
        phone=user.phone,
        name=user.name,
        role=user.role,
        password_hash=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token = auth.create_access_token(
        data={"sub": new_user.phone, "role": new_user.role}
    )
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "role": new_user.role,
        "user_id": new_user.id,
        "name": new_user.name
    }

@app.post("/auth/login", response_model=schemas.Token)
def login(user_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.phone == user_data.phone).first()
    if not user or not auth.verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect phone or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth.create_access_token(
        data={"sub": user.phone, "role": user.role}
    )
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "role": user.role,
        "user_id": user.id,
        "name": user.name
    }

# --- Student Interfaces ---

@app.post("/activity/finish", response_model=schemas.ActivityOut)
def finish_activity(
    activity_in: schemas.ActivityFinish,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Create Activity
    db_activity = models.Activity(
        user_id=current_user.id,
        type=activity_in.type,
        source=activity_in.source,
        status="finished", # 默认为完成，等待审核或自动通过
        started_at=activity_in.started_at,
        ended_at=activity_in.ended_at
    )
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)

    # 2. Create Metrics
    db_metrics = models.ActivityMetrics(
        activity_id=db_activity.id,
        **activity_in.metrics.dict()
    )
    db.add(db_metrics)

    # 3. Create Evidence (if any)
    for evidence in activity_in.evidence:
        db_evidence = models.ActivityEvidence(
            activity_id=db_activity.id,
            **evidence.dict()
        )
        db.add(db_evidence)
    
    db.commit()
    db.refresh(db_activity)
    return db_activity

@app.get("/activity/history", response_model=schemas.ActivityListResponse)
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

# --- Teacher Interfaces ---

@app.get("/teacher/activities", response_model=schemas.TeacherActivityListResponse)
def get_teacher_activities(
    page: int = 1,
    size: int = 20,
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    # 获取所有未审核或已审核的记录，按时间倒序
    # 对于同一个学生，如果有多条待审核记录，我们这里应该怎么处理？
    # 按照需求：同一个学生提交了三次数据不应该并行在同一条里面吗 -> 这句话意味着用户希望看到分组后的数据，
    # 但实际上审批流通常是针对单次活动的。如果用户希望“合并”，可能是指UI上的折叠，或者是逻辑上的最新一条覆盖？
    # “而且怎么查看学生跑了多少” -> 这暗示用户想看累计数据或者历史记录。
    
    # 目前的实现是平铺所有 Activity。如果用户觉得乱，可能是因为同一个学生刷屏了。
    # 改进方案：
    # 1. 保持 /teacher/activities 为平铺流（适合审批流）。
    # 2. 前端可以做 UI 分组。
    # 3. 提供 /teacher/students/{student_id}/activities 接口来查看特定学生的记录（已计划）。
    
    # 暂时保持平铺，但确保包含 metrics 详细信息。
    
    query = db.query(models.Activity)
    total = query.count()
    activities = query.order_by(models.Activity.started_at.desc()).offset((page - 1) * size).limit(size).all()
    
    return {
        "items": activities,
        "total": total,
        "page": page,
        "size": size
    }

@app.get("/teacher/student/{student_id}/activities", response_model=schemas.ActivityListResponse)
def get_student_activities_for_teacher(
    student_id: int,
    page: int = 1,
    size: int = 20,
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    query = db.query(models.Activity).filter(models.Activity.user_id == student_id)
    total = query.count()
    activities = query.order_by(models.Activity.started_at.desc()).offset((page - 1) * size).limit(size).all()
    
    return {
        "items": activities,
        "total": total,
        "page": page,
        "size": size
    }

@app.post("/teacher/activity/{activity_id}/approve", response_model=schemas.ActivityOut)
def approve_activity(
    activity_id: int,
    approval: schemas.ApproveRequest, # 虽然只允许 approved，但为了扩展性还是接收个 body 吧，或者直接忽略 body
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    activity = db.query(models.Activity).filter(models.Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Check if already reviewed
    if activity.review:
        raise HTTPException(status_code=400, detail="Activity already reviewed")

    # Update activity status
    activity.status = "approved"
    
    # Create Review Record
    review = models.ActivityReview(
        activity_id=activity.id,
        teacher_id=current_user.id,
        result="approved"
    )
    db.add(review)
    db.commit()
    db.refresh(activity)
    
    return activity

@app.post("/teacher/tasks", response_model=schemas.TaskOut)
def create_task(
    task_in: schemas.TaskCreate,
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    new_task = models.Task(
        title=task_in.title,
        type=task_in.type,
        min_distance=task_in.min_distance,
        min_duration=task_in.min_duration,
        min_count=task_in.min_count,
        deadline=task_in.deadline,
        description=task_in.description,
        target_group=task_in.target_group,
        created_by=current_user.id
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@app.get("/teacher/tasks", response_model=schemas.TaskListResponse)
def get_teacher_tasks(
    page: int = 1,
    size: int = 20,
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    query = db.query(models.Task).filter(models.Task.created_by == current_user.id)
    total = query.count()
    tasks = query.order_by(models.Task.id.desc()).offset((page - 1) * size).limit(size).all()
    
    # Calculate stats for each task
    # Note: This is N+1 query, but acceptable for MVP with pagination (20 items)
    tasks_with_stats = []
    
    # Get all students count once
    total_students = db.query(models.User).filter(models.User.role == "student").count()
    
    for task in tasks:
        # Reusing similar logic to get_task_detail but optimized for counting only
        # We need to find how many students completed this task
        
        # Get all activities that match this task type and time range
        act_query = db.query(models.Activity).filter(
            models.Activity.type == task.type
        )
        if task.created_at:
             act_query = act_query.filter(models.Activity.started_at >= task.created_at)
        if task.deadline:
            act_query = act_query.filter(models.Activity.started_at <= task.deadline)
            
        activities = act_query.all()
        
        # Group by user_id to find unique completers
        # A student might have multiple activities, we only need to know if ONE of them qualifies
        student_activities = {}
        for act in activities:
            if act.user_id not in student_activities:
                student_activities[act.user_id] = []
            student_activities[act.user_id].append(act)
            
        completed_count = 0
        
        for student_id, acts in student_activities.items():
            is_completed = False
            for act in acts:
                metrics = act.metrics
                if not metrics:
                    continue
                
                if task.min_distance and task.min_distance > 0:
                    if (metrics.distance or 0) < task.min_distance:
                        continue
                
                if task.min_duration and task.min_duration > 0:
                    if (metrics.duration or 0) < (task.min_duration * 60):
                        continue
                
                if task.min_count and task.min_count > 0:
                    if (metrics.count or 0) < task.min_count:
                        continue
                        
                is_completed = True
                break
            
            if is_completed:
                completed_count += 1
        
        task_dict = task.__dict__
        task_dict["total_students"] = total_students
        task_dict["completed_count"] = completed_count
        tasks_with_stats.append(task_dict)

    return {
        "items": tasks_with_stats,
        "total": total,
        "page": page,
        "size": size
    }

@app.delete("/teacher/tasks/{task_id}")
def delete_task(
    task_id: int,
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    return {"ok": True}

@app.get("/teacher/tasks/{task_id}", response_model=schemas.TaskDetailStats)
def get_task_detail(
    task_id: int,
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Get all students
    # In a real app, we might filter by target_group
    students = db.query(models.User).filter(models.User.role == "student").all()
    
    student_statuses = []
    completed_count = 0
    
    for student in students:
        # Find qualifying activity
        act_query = db.query(models.Activity).filter(
            models.Activity.user_id == student.id,
            models.Activity.type == task.type
        )
        
        if task.created_at:
             act_query = act_query.filter(models.Activity.started_at >= task.created_at)
        
        if task.deadline:
            act_query = act_query.filter(models.Activity.started_at <= task.deadline)
            
        activities = act_query.all()
        
        is_completed = False
        completed_activity = None
        
        for act in activities:
            metrics = act.metrics
            if not metrics:
                continue
                
            # Distance (km)
            if task.min_distance and task.min_distance > 0:
                if (metrics.distance or 0) < task.min_distance:
                    continue
            
            # Duration (minutes vs seconds)
            if task.min_duration and task.min_duration > 0:
                if (metrics.duration or 0) < (task.min_duration * 60):
                    continue
            
            # Count
            if task.min_count and task.min_count > 0:
                if (metrics.count or 0) < task.min_count:
                    continue
                    
            is_completed = True
            completed_activity = act
            break
        
        status = "pending"
        metric_val = "-"
        completed_at = None
        
        if is_completed:
            status = "completed"
            completed_count += 1
            completed_at = completed_activity.ended_at
            if task.type == 'run':
                metric_val = f"{completed_activity.metrics.distance} km"
            else:
                metric_val = f"{completed_activity.metrics.count} 次"
        
        student_statuses.append(schemas.StudentCompletionStatus(
            student_id=student.id,
            student_name=student.name,
            status=status,
            completed_at=completed_at,
            metric_value=metric_val
        ))
        
    return {
        **task.__dict__,
        "total_students": len(students),
        "completed_count": completed_count,
        "student_statuses": student_statuses
    }

@app.get("/student/tasks", response_model=schemas.StudentTaskListResponse)
def get_student_tasks(
    page: int = 1,
    size: int = 20,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    from datetime import datetime
    now = datetime.utcnow()

    query = db.query(models.Task)
    total = query.count()
    tasks = query.order_by(models.Task.id.desc()).offset((page - 1) * size).limit(size).all()
    
    student_tasks = []
    
    for task in tasks:
        status = "pending"
        progress = 0.0
        
        if task.deadline and task.deadline < now:
            status = "expired"
        
        # Check completion
        # Activity started after task creation (or check all if created_at is null/old)
        # Use task.created_at if available, else ignore start time check (or use task logic)
        act_query = db.query(models.Activity).filter(
            models.Activity.user_id == current_user.id,
            models.Activity.type == task.type
        )
        
        if task.created_at:
             act_query = act_query.filter(models.Activity.started_at >= task.created_at)
        
        if task.deadline:
            act_query = act_query.filter(models.Activity.started_at <= task.deadline)
            
        activities = act_query.all()
        
        is_completed = False
        
        for act in activities:
            # Check requirements
            metrics = act.metrics
            if not metrics:
                continue
                
            # Distance (km)
            if task.min_distance and task.min_distance > 0:
                if (metrics.distance or 0) < task.min_distance:
                    continue
            
            # Duration (minutes vs seconds)
            if task.min_duration and task.min_duration > 0:
                if (metrics.duration or 0) < (task.min_duration * 60):
                    continue
            
            # Count
            if task.min_count and task.min_count > 0:
                if (metrics.count or 0) < task.min_count:
                    continue
                    
            is_completed = True
            break
        
        if is_completed:
            status = "completed"
            progress = 100.0
            
        # Construct response object
        # We need to copy task data + extra fields
        task_dict = {
            "id": task.id,
            "title": task.title,
            "type": task.type,
            "min_distance": task.min_distance,
            "min_duration": task.min_duration,
            "min_count": task.min_count,
            "deadline": task.deadline,
            "description": task.description,
            "target_group": task.target_group,
            "created_by": task.created_by,
            "status": status,
            "progress": progress
        }
        student_tasks.append(task_dict)

    return {
        "items": student_tasks,
        "total": total,
        "page": page,
        "size": size
    }
