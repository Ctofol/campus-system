from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Body
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from datetime import datetime, timedelta
import shutil
import os
import uuid
import random
import string
import base64
import hashlib
from captcha.image import ImageCaptcha
from . import models, schemas, auth, database
from .routers import admin

# 初始化数据库表
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Campus Sports Health MVP")

app.include_router(admin.router)

# Mount uploads directory
if not os.path.exists("uploads"):
    os.makedirs("uploads")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "*"
    ],
    allow_origin_regex=r"http://localhost:\d+|http://127\.0\.0\.1:\d+|http://192\.168\.\d+\.\d+:\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition", "content-disposition"]
)

# Dependency
get_db = database.get_db

# --- Common Interfaces ---
CAPTCHA_SECRET = "lingxi_sports_mvp_secret_salt_2026"

@app.get("/common/captcha")
def get_captcha():
    # Generate 4 random chars
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    
    # Generate image
    image = ImageCaptcha(width=120, height=50)
    data = image.generate(code)
    
    # Encode to base64
    base64_str = base64.b64encode(data.getvalue()).decode('utf-8')
    image_data = f"data:image/png;base64,{base64_str}"
    
    # Generate key (simple stateless verification)
    # Key = MD5(Upper(Code) + Secret)
    key_src = code.upper() + CAPTCHA_SECRET
    key = hashlib.md5(key_src.encode('utf-8')).hexdigest()
    
    return {"image": image_data, "key": key}

# --- Auth Interfaces ---

@app.post("/auth/register", response_model=schemas.Token)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # 1. Verify Captcha
    verify_src = user.captcha_code.upper() + CAPTCHA_SECRET
    expected_key = hashlib.md5(verify_src.encode('utf-8')).hexdigest()
    
    if expected_key != user.captcha_key:
        raise HTTPException(status_code=400, detail="验证码错误")

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
    
    class_name = user.student_class.name if user.student_class else None
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "role": user.role,
        "user_id": user.id,
        "name": user.name,
        "class_name": class_name,
        "student_id": user.student_id
    }

@app.get("/users/profile", response_model=schemas.UserProfile)
def get_my_profile(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    # Ensure fresh data
    db.refresh(current_user)
    
    profile_data = {
        "id": current_user.id,
        "name": current_user.name,
        "phone": current_user.phone,
        "role": current_user.role,
        "student_id": current_user.student_id,
        "group_name": current_user.group_name,
        "health_status": current_user.health_status,
        "class_name": current_user.student_class.name if current_user.student_class else None
    }
    return profile_data

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

# --- Class Interfaces ---

@app.get("/teacher/available_classes", response_model=List[schemas.ClassOut])
def get_available_classes(
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    classes = db.query(models.Class).filter(models.Class.teacher_id == None).all()
    results = []
    for c in classes:
        c_dict = c.__dict__
        c_dict["student_count"] = len(c.students)
        results.append(c_dict)
    return results

@app.post("/teacher/classes/bind")
def bind_classes(
    bind_data: schemas.ClassBind,
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    classes = db.query(models.Class).filter(models.Class.id.in_(bind_data.class_ids)).all()
    for cls in classes:
        if cls.teacher_id is not None and cls.teacher_id != current_user.id:
            continue
        cls.teacher_id = current_user.id
    db.commit()
    return {"ok": True}

@app.get("/teacher/classes", response_model=List[schemas.ClassOut])
def get_classes(
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    classes = db.query(models.Class).filter(models.Class.teacher_id == current_user.id).all()
    results = []
    for c in classes:
        c_dict = c.__dict__
        c_dict["student_count"] = len(c.students)
        results.append(c_dict)
    return results

@app.delete("/teacher/classes/{class_id}")
def unbind_class(
    class_id: int,
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    cls = db.query(models.Class).filter(models.Class.id == class_id, models.Class.teacher_id == current_user.id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")
    
    cls.teacher_id = None
    db.commit()
    return {"ok": True}

@app.get("/teacher/classes/{class_id}", response_model=schemas.ClassDetail)
def get_class_detail(
    class_id: int,
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    cls = db.query(models.Class).filter(models.Class.id == class_id).first()
    if not cls:
         raise HTTPException(status_code=404, detail="Class not found")
    
    if cls.teacher_id != current_user.id:
         raise HTTPException(status_code=403, detail="Not authorized to view this class")
    
    c_dict = cls.__dict__
    c_dict["student_count"] = len(cls.students)
    c_dict["students"] = cls.students
    return c_dict

@app.put("/teacher/classes/{class_id}", response_model=schemas.ClassOut)
def update_class(
    class_id: int,
    class_in: schemas.ClassCreate,
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    cls = db.query(models.Class).filter(models.Class.id == class_id, models.Class.teacher_id == current_user.id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")
        
    cls.name = class_in.name
    db.commit()
    db.refresh(cls)
    
    # Manually attach student count
    c_dict = cls.__dict__
    c_dict["student_count"] = len(cls.students)
    return c_dict

@app.get("/teacher/classes/{class_id}/students", response_model=List[schemas.StudentDetail])
def get_class_students(
    class_id: int,
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    cls = db.query(models.Class).filter(models.Class.id == class_id, models.Class.teacher_id == current_user.id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")
    
    return cls.students

@app.post("/teacher/classes/{class_id}/students")
def add_student_to_class(
    class_id: int,
    phone: str = Body(..., embed=True),
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    cls = db.query(models.Class).filter(models.Class.id == class_id, models.Class.teacher_id == current_user.id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")
        
    student = db.query(models.User).filter(models.User.phone == phone, models.User.role == "student").first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    student.class_id = class_id
    db.commit()
    return {"ok": True}

@app.delete("/teacher/classes/{class_id}/students/{student_id}")
def remove_student_from_class(
    class_id: int,
    student_id: int,
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    cls = db.query(models.Class).filter(models.Class.id == class_id, models.Class.teacher_id == current_user.id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")
        
    student = db.query(models.User).filter(models.User.id == student_id, models.User.class_id == class_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found in this class")
        
    student.class_id = None
    db.commit()
    return {"ok": True}

@app.get("/teacher/classes/{class_id}/stats")
def get_class_stats(
    class_id: int,
    task_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    cls = db.query(models.Class).filter(models.Class.id == class_id, models.Class.teacher_id == current_user.id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")
    
    # Pre-fetch task if provided to filter by task type/window
    task = None
    if task_id:
        task = db.query(models.Task).filter(models.Task.id == task_id).first()

    # 简单统计：总里程，总运动次数，人均数据
    total_distance = 0.0
    total_activities = 0
    student_stats = []
    
    for student in cls.students:
        query = db.query(models.Activity).filter(models.Activity.user_id == student.id)
        
        # Filter by Task
        if task:
            query = query.filter(models.Activity.type == task.type)
            if task.created_at:
                 query = query.filter(models.Activity.started_at >= task.created_at)
            if task.deadline:
                query = query.filter(models.Activity.started_at <= task.deadline)

        # Filter by Time Range
        if start_date:
            query = query.filter(models.Activity.started_at >= start_date)
        if end_date:
             query = query.filter(models.Activity.started_at <= end_date)

        activities = query.all()
        s_dist = 0.0
        s_count = len(activities)
        for act in activities:
            if act.metrics and act.metrics.distance:
                s_dist += act.metrics.distance
        
        total_distance += s_dist
        total_activities += s_count
        student_stats.append({
            "id": student.id,
            "name": student.name,
            "distance": s_dist,
            "count": s_count
        })
        
    return {
        "class_name": cls.name,
        "student_count": len(cls.students),
        "total_distance": total_distance,
        "total_activities": total_activities,
        "student_stats": student_stats
    }

# --- Teacher Interfaces ---

@app.get("/teacher/dashboard/stats", response_model=schemas.TeacherDashboardOut)
def get_teacher_dashboard_stats(
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    # --- 1. Stats Calculation ---
    
    # 1. Student Count
    student_count = db.query(models.User).filter(models.User.role == "student").count()
    
    # 2. Pending Approvals (Health Requests + Pending Activities)
    pending_health = db.query(models.HealthRequest).filter(models.HealthRequest.status == "pending").count()
    pending_activities = db.query(models.Activity).filter(models.Activity.status == "pending_review").count()
    pending_approvals = pending_health + pending_activities
    
    # 3. Abnormal Count
    abnormal_count = db.query(models.User).filter(
        models.User.role == "student",
        models.User.health_status != "normal"
    ).count()
    
    # 4. Today Check-in
    today = datetime.utcnow().date()
    today_start = datetime(today.year, today.month, today.day)
    today_checkin = db.query(models.Activity).filter(
        models.Activity.started_at >= today_start
    ).count()
    
    # 5. Task Count
    task_count = db.query(models.Task).count()
    
    # --- 2. Todos Generation ---
    todos = []
    
    # A. Pending Health Requests
    pending_reqs = db.query(models.HealthRequest).filter(
        models.HealthRequest.status == "pending"
    ).order_by(models.HealthRequest.created_at.desc()).limit(5).all()
    
    for req in pending_reqs:
        student = db.query(models.User).filter(models.User.id == req.student_id).first()
        student_name = student.name if student else "Unknown"
        todos.append({
            "id": f"health_{req.id}",
            "title": "请假审批",
            "type": "approval",
            "desc": f"{student_name} 申请 {req.type} ({req.reason})",
            "time": req.created_at.strftime("%H:%M"),
            "path": "/pages/teacher/students/students?action=approval",
            "priority": "high"
        })

    # A2. Pending Activities
    pending_acts = db.query(models.Activity).filter(
        models.Activity.status == "pending_review"
    ).order_by(models.Activity.started_at.desc()).limit(5).all()
    
    for act in pending_acts:
        student = db.query(models.User).filter(models.User.id == act.user_id).first()
        student_name = student.name if student else "Unknown"
        todos.append({
            "id": f"activity_{act.id}",
            "title": "运动审批",
            "type": "approval",
            "desc": f"{student_name} 提交 {act.type} 记录",
            "time": act.started_at.strftime("%H:%M"),
            "path": "/pages/teacher/approve/approve",
            "priority": "high"
        })
        
    # B. Tasks nearing deadline (< 24h)
    tomorrow = datetime.utcnow() + timedelta(days=1)
    near_deadline_tasks = db.query(models.Task).filter(
        models.Task.deadline != None,
        models.Task.deadline > datetime.utcnow(),
        models.Task.deadline < tomorrow
    ).all()
    
    for task in near_deadline_tasks:
        todos.append({
            "id": f"task_{task.id}",
            "title": "任务即将截止",
            "type": "task",
            "desc": f"任务 '{task.title}' 将于24小时内截止",
            "time": task.deadline.strftime("%m-%d %H:%M"),
            "path": f"/pages/teacher/tasks/detail?id={task.id}",
            "priority": "medium"
        })
    
    # C. Abnormal Students (if any)
    if abnormal_count > 0:
        todos.append({
            "id": "abnormal_alert",
            "title": "异常状态关注",
            "type": "task",
            "desc": f"有 {abnormal_count} 名学生处于异常/请假状态，请关注",
            "time": datetime.utcnow().strftime("%H:%M"),
            "path": "/pages/teacher/students/students?filter=abnormal",
            "priority": "high"
        })

    return {
        "stats": {
            "student_count": student_count,
            "today_checkin": today_checkin,
            "abnormal_count": abnormal_count,
            "pending_approvals": pending_approvals,
            "avg_pace": "5'45\"", # Mock
            "task_count": task_count,
            "compliance_rate": 92 # Mock
        },
        "todos": todos
    }

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

@app.get("/teacher/stats", response_model=schemas.TeacherStatsOut)
def get_teacher_stats(
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    # 1. Student Count
    student_count = db.query(models.User).filter(models.User.role == "student").count()
    
    # 2. Pending Approvals (Health Requests)
    pending_approvals = db.query(models.HealthRequest).filter(models.HealthRequest.status == "pending").count()
    
    # 3. Abnormal Count
    abnormal_count = db.query(models.User).filter(
        models.User.role == "student",
        models.User.health_status != "normal"
    ).count()
    
    # 4. Today Check-in (Activities today)
    today = datetime.utcnow().date()
    today_start = datetime(today.year, today.month, today.day)
    today_checkin = db.query(models.Activity).filter(
        models.Activity.started_at >= today_start
    ).count()
    
    # 5. Task Count
    task_count = db.query(models.Task).count()
    
    return {
        "student_count": student_count,
        "today_checkin": today_checkin,
        "abnormal_count": abnormal_count,
        "pending_approvals": pending_approvals,
        "avg_pace": "5'45\"", # Mock for now
        "task_count": task_count,
        "compliance_rate": 92 # Mock for now
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



# --- Advanced Student Management ---

@app.get("/teacher/students", response_model=List[schemas.StudentDetail])
def get_all_students(
    page: int = 1,
    size: int = 20,
    class_id: Optional[int] = None,
    name: Optional[str] = None,
    student_id: Optional[str] = None,
    status: Optional[str] = None, # 'normal', 'leave', 'injured'
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    # Only show students in classes managed by the current teacher
    query = db.query(models.User).join(models.Class, models.User.class_id == models.Class.id).filter(
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
    
    total = query.count()
    students = query.offset((page - 1) * size).limit(size).all()
    return students

@app.get("/teacher/students/abnormal", response_model=List[schemas.StudentDetail])
def get_abnormal_students(
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    students = db.query(models.User).join(models.Class, models.User.class_id == models.Class.id).filter(
        models.User.role == "student",
        models.Class.teacher_id == current_user.id,
        models.User.health_status != "normal"
    ).all()
    return students

@app.get("/teacher/students/{student_id}", response_model=schemas.StudentDetail)
def get_student_detail(
    student_id: int,
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    student = db.query(models.User).filter(models.User.id == student_id, models.User.role == "student").first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@app.put("/teacher/students/{student_id}", response_model=schemas.StudentDetail)
def update_student(
    student_id: int,
    student_in: schemas.StudentUpdate,
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    student = db.query(models.User).filter(models.User.id == student_id, models.User.role == "student").first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
        
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

@app.post("/teacher/students/bulk-update", status_code=200)
def bulk_update_students(
    update_in: schemas.BulkUpdateStudent,
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    query = db.query(models.User).filter(
        models.User.id.in_(update_in.student_ids),
        models.User.role == "student"
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
        
    # Using synchronize_session=False for efficiency, but we need to verify if any rows matched
    rows_updated = query.update(update_data, synchronize_session=False)
    db.commit()
    
    return {"message": "Success", "updated_count": rows_updated}

@app.post("/teacher/students/export")
def export_students(
    export_in: schemas.BulkUpdateStudent, # Reusing this schema as it has student_ids and filters
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    import csv
    import io
    from fastapi.responses import StreamingResponse

    query = db.query(models.User).filter(models.User.role == "student")
    
    # If specific IDs are provided, export those
    if export_in.student_ids:
        query = query.filter(models.User.id.in_(export_in.student_ids))
    else:
        # Otherwise apply filters
        if export_in.class_id:
            query = query.filter(models.User.class_id == export_in.class_id)
        if export_in.health_status:
            query = query.filter(models.User.health_status == export_in.health_status)
        if export_in.group_name:
            query = query.filter(models.User.group_name == export_in.group_name)
        
    students = query.all()
    
    # Generate CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['ID', 'Name', 'Student ID', 'Phone', 'Class ID', 'Group', 'Health Status', 'Abnormal Reason'])
    
    for s in students:
        writer.writerow([
            s.id,
            s.name,
            s.student_id or '',
            s.phone,
            s.class_id or '',
            s.group_name or '',
            s.health_status,
            s.abnormal_reason or ''
        ])
        
    output.seek(0)
    
    response = StreamingResponse(iter([output.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=students_export.csv"
    return response



# --- Health Status Management ---

@app.post("/student/health/request", response_model=schemas.HealthRequestOut)
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
        
    new_req = models.HealthRequest(
        student_id=current_user.id,
        type=request_in.type,
        reason=request_in.reason,
        status="pending"
    )
    db.add(new_req)
    db.commit()
    db.refresh(new_req)
    return new_req

@app.get("/student/health/requests", response_model=List[schemas.HealthRequestOut])
def get_my_health_requests(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can view their health requests")
        
    requests = db.query(models.HealthRequest).filter(
        models.HealthRequest.student_id == current_user.id
    ).order_by(models.HealthRequest.created_at.desc()).all()
    
    return requests

@app.get("/teacher/health/requests", response_model=List[schemas.HealthRequestOut])
def get_pending_health_requests(
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    requests = db.query(models.HealthRequest).filter(
        models.HealthRequest.status == "pending"
    ).all()
    return requests

@app.put("/teacher/health/requests/{request_id}/review")
def review_health_request(
    request_id: int,
    status: str = Body(..., embed=True), # 'approved' or 'rejected'
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    if status not in ["approved", "rejected"]:
        raise HTTPException(status_code=400, detail="Invalid status")
        
    req = db.query(models.HealthRequest).filter(models.HealthRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
        
    req.status = status
    
    # If approved, update student status
    if status == "approved":
        student = db.query(models.User).filter(models.User.id == req.student_id).first()
        if student:
            if req.type == "leave":
                student.health_status = "leave"
                student.abnormal_reason = req.reason
            elif req.type == "injury":
                student.health_status = "injured"
                student.abnormal_reason = req.reason
                
    db.commit()
    return {"ok": True}

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
        class_id=task_in.class_id,
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
    status: Optional[str] = None, # 'active', 'ended'
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    query = db.query(models.Task).filter(models.Task.created_by == current_user.id)
    
    # Default to active tasks if status is not provided or explicitly 'active'
    if status == 'ended':
        query = query.filter(models.Task.deadline < datetime.utcnow())
    elif status == 'active' or status is None:
        # Show tasks with no deadline OR deadline in future
        query = query.filter(or_(models.Task.deadline == None, models.Task.deadline > datetime.utcnow()))
        
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
    
    # 仅显示本班老师发布的任务或全局任务（class_id 为 NULL）
    if current_user.class_id:
        cls = db.query(models.Class).filter(models.Class.id == current_user.class_id).first()
        teacher_id = cls.teacher_id if cls else None
        query = query.filter(or_(models.Task.class_id == current_user.class_id, models.Task.class_id == None))
        if teacher_id:
            query = query.filter(models.Task.created_by == teacher_id)
    else:
        # 没有班级的学生仅显示全局任务
        query = query.filter(models.Task.class_id == None)

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

# --- Checkpoint Interfaces ---

@app.get("/checkpoints", response_model=List[schemas.CheckpointOut])
def get_checkpoints(
    db: Session = Depends(get_db)
):
    return db.query(models.Checkpoint).all()

@app.post("/checkpoints", response_model=schemas.CheckpointOut)
def create_checkpoint(
    checkpoint_in: schemas.CheckpointCreate,
    current_user: models.User = Depends(auth.get_current_teacher), # Only teacher can create
    db: Session = Depends(get_db)
):
    db_checkpoint = models.Checkpoint(**checkpoint_in.dict())
    db.add(db_checkpoint)
    db.commit()
    db.refresh(db_checkpoint)
    return db_checkpoint

@app.post("/activity/checkin")
def check_in(
    checkin_in: schemas.CheckInRequest,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    # Validate range
    checkpoint = db.query(models.Checkpoint).filter(models.Checkpoint.id == checkin_in.checkpoint_id).first()
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")
        
    # Simple distance check (Haversine approx or simple euclidean for small distances)
    # Using Haversine formula for accuracy
    import math
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

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    UPLOAD_DIR = "uploads"
    # Ensure directory exists (already done in startup but good to be safe)
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
    
    # Generate unique filename to prevent overwrite
    file_extension = os.path.splitext(file.filename)[1]
    if not file_extension:
        file_extension = ".jpg" # Default to jpg if no extension
        
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not upload file: {str(e)}")
        
    # Return URL (relative path)
    return {
        "url": f"/uploads/{unique_filename}", 
        "filename": unique_filename,
        "original_filename": file.filename
    }

if __name__ == "__main__":
    import uvicorn
    # Allow access from all IPs for local testing
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
