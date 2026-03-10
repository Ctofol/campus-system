from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import pandas as pd
import io

from .database import get_db
from . import models, schemas, auth

models.Base.metadata.create_all(bind=auth.database.engine)

app = FastAPI(title="Campus Admin API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth
@app.post("/auth/login", response_model=schemas.Token)
def login(user_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.phone == user_data.phone).first()
    if not user or not auth.verify_password(user_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect phone or password")
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access only")
    access_token = auth.create_access_token(data={"sub": user.phone, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer", "role": user.role, "name": user.name}

@app.post("/auth/refresh")
def refresh_token(current_user: models.User = Depends(auth.get_current_admin)):
    access_token = auth.create_access_token(data={"sub": current_user.phone, "role": current_user.role})
    return {"access_token": access_token, "token_type": "bearer"}

# Dashboard
@app.get("/admin/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_admin)):
    total_students = db.query(func.count(models.User.id)).filter(models.User.role == "student").scalar()
    total_teachers = db.query(func.count(models.User.id)).filter(models.User.role == "teacher").scalar()
    total_classes = db.query(func.count(models.Class.id)).scalar()
    pending_health = db.query(models.HealthRequest).filter(models.HealthRequest.status == "pending").count()
    pending_activities = db.query(models.Activity).filter(models.Activity.status == "pending_review").count()
    return {
        "total_students": total_students,
        "total_teachers": total_teachers,
        "total_classes": total_classes,
        "pending_approvals": pending_health + pending_activities,
    }

# Classes
@app.get("/admin/classes", response_model=List[schemas.ClassOut])
def get_classes(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_admin)):
    classes = db.query(models.Class).all()
    for cls in classes:
        cls.student_count = db.query(func.count(models.User.id)).filter(models.User.class_id == cls.id).scalar()
    return classes

@app.post("/admin/classes", response_model=schemas.ClassOut)
def create_class(class_in: schemas.ClassCreate, teacher_id: Optional[int] = None, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_admin)):
    if db.query(models.Class).filter(models.Class.name == class_in.name).first():
        raise HTTPException(status_code=400, detail="Class already exists")
    new_class = models.Class(name=class_in.name, teacher_id=teacher_id)
    db.add(new_class)
    db.commit()
    db.refresh(new_class)
    new_class.student_count = 0
    return new_class

@app.delete("/admin/classes/{class_id}")
def delete_class(class_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_admin)):
    cls = db.query(models.Class).filter(models.Class.id == class_id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")
    count = db.query(func.count(models.User.id)).filter(models.User.class_id == class_id).scalar()
    if count > 0:
        raise HTTPException(status_code=400, detail="Cannot delete class with students")
    db.delete(cls)
    db.commit()
    return {"message": "Class deleted"}

# Users
@app.get("/admin/users", response_model=List[schemas.UserProfile])
def get_users(role: Optional[str] = None, class_id: Optional[int] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_admin)):
    query = db.query(models.User)
    if role:
        query = query.filter(models.User.role == role)
    if class_id:
        query = query.filter(models.User.class_id == class_id)
    users = query.offset(skip).limit(limit).all()
    for user in users:
        if user.class_id:
            cls = db.query(models.Class).filter(models.Class.id == user.class_id).first()
            user.class_name = cls.name if cls else None
    return users

@app.post("/admin/users", response_model=schemas.UserProfile)
def create_user(user_in: schemas.UserCreate, class_id: Optional[int] = None, student_id: Optional[str] = None, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_admin)):
    if db.query(models.User).filter(models.User.phone == user_in.phone).first():
        raise HTTPException(status_code=400, detail="Phone already registered")
    new_user = models.User(
        phone=user_in.phone, name=user_in.name,
        password_hash=auth.get_password_hash(user_in.password),
        role=user_in.role, class_id=class_id, student_id=student_id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.delete("/admin/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_admin)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.role == "admin":
        raise HTTPException(status_code=400, detail="Cannot delete admin")
    db.delete(user)
    db.commit()
    return {"message": "User deleted"}

@app.post("/admin/users/{user_id}/reset-password")
def reset_password(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_admin)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.password_hash = auth.get_password_hash("123456")
    db.commit()
    return {"message": "Password reset to 123456"}

# Import
@app.post("/admin/import/students")
async def import_students(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_admin)):
    contents = await file.read()
    df = pd.read_excel(io.BytesIO(contents))
    required = ['姓名', '手机号', '密码', '学号', '所属班级名称']
    if not all(c in df.columns for c in required):
        raise HTTPException(status_code=400, detail=f"缺少列: {required}")
    results = {"success": 0, "failed": 0, "errors": []}
    for i, row in df.iterrows():
        try:
            phone = str(row['手机号']).strip()
            if db.query(models.User).filter(models.User.phone == phone).first():
                raise ValueError("手机号已存在")
            class_name = str(row['所属班级名称']).strip()
            cls = db.query(models.Class).filter(models.Class.name == class_name).first()
            if not cls:
                cls = models.Class(name=class_name)
                db.add(cls); db.commit(); db.refresh(cls)
            db.add(models.User(
                phone=phone, name=str(row['姓名']).strip(),
                password_hash=auth.get_password_hash(str(row['密码']).strip()),
                role="student", student_id=str(row['学号']).strip(), class_id=cls.id
            ))
            db.commit()
            results["success"] += 1
        except Exception as e:
            db.rollback()
            results["failed"] += 1
            results["errors"].append({"row": i+2, "error": str(e)})
    return results

@app.post("/admin/import/teachers")
async def import_teachers(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_admin)):
    contents = await file.read()
    df = pd.read_excel(io.BytesIO(contents))
    required = ['姓名', '手机号', '密码', '工号']
    if not all(c in df.columns for c in required):
        raise HTTPException(status_code=400, detail=f"缺少列: {required}")
    results = {"success": 0, "failed": 0, "errors": []}
    for i, row in df.iterrows():
        try:
            phone = str(row['手机号']).strip()
            if db.query(models.User).filter(models.User.phone == phone).first():
                raise ValueError("手机号已存在")
            db.add(models.User(
                phone=phone, name=str(row['姓名']).strip(),
                password_hash=auth.get_password_hash(str(row['密码']).strip()),
                role="teacher", student_id=str(row['工号']).strip()
            ))
            db.commit()
            results["success"] += 1
        except Exception as e:
            db.rollback()
            results["failed"] += 1
            results["errors"].append({"row": i+2, "error": str(e)})
    return results

@app.get("/admin/import/template/students")
def student_template(current_user: models.User = Depends(auth.get_current_admin)):
    df = pd.DataFrame(columns=["姓名", "手机号", "密码", "学号", "所属班级名称"])
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as w: df.to_excel(w, index=False)
    buf.seek(0)
    return StreamingResponse(buf, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=student_template.xlsx"})

@app.get("/admin/import/template/teachers")
def teacher_template(current_user: models.User = Depends(auth.get_current_admin)):
    df = pd.DataFrame(columns=["姓名", "手机号", "密码", "工号"])
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as w: df.to_excel(w, index=False)
    buf.seek(0)
    return StreamingResponse(buf, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=teacher_template.xlsx"})
