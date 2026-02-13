
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import pandas as pd
import io

from ..database import get_db
from .. import models, schemas, auth

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    responses={404: {"description": "Not found"}},
)

# Dependency to check if user is admin
async def get_current_admin(current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation not permitted"
        )
    return current_user

# --- Classes Management ---

@router.get("/classes", response_model=List[schemas.ClassOut])
def get_classes(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin)
):
    classes = db.query(models.Class).offset(skip).limit(limit).all()
    # Calculate student count manually or rely on property if exists (schema has student_count)
    for cls in classes:
        cls.student_count = db.query(func.count(models.User.id)).filter(models.User.class_id == cls.id).scalar()
    return classes

@router.post("/classes", response_model=schemas.ClassOut)
def create_class(
    class_in: schemas.ClassCreate, 
    teacher_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin)
):
    db_class = db.query(models.Class).filter(models.Class.name == class_in.name).first()
    if db_class:
        raise HTTPException(status_code=400, detail="Class already exists")
    
    new_class = models.Class(name=class_in.name, teacher_id=teacher_id)
    db.add(new_class)
    db.commit()
    db.refresh(new_class)
    new_class.student_count = 0
    return new_class

@router.delete("/classes/{class_id}")
def delete_class(
    class_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin)
):
    db_class = db.query(models.Class).filter(models.Class.id == class_id).first()
    if not db_class:
        raise HTTPException(status_code=404, detail="Class not found")
    
    # Check if class has students
    student_count = db.query(func.count(models.User.id)).filter(models.User.class_id == class_id).scalar()
    if student_count > 0:
        raise HTTPException(status_code=400, detail="Cannot delete class with students")
        
    db.delete(db_class)
    db.commit()
    return {"message": "Class deleted"}

# --- Users Management ---

@router.get("/users", response_model=List[schemas.UserProfile])
def get_users(
    role: Optional[str] = None,
    class_id: Optional[int] = None,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin)
):
    query = db.query(models.User)
    if role:
        query = query.filter(models.User.role == role)
    if class_id:
        query = query.filter(models.User.class_id == class_id)
        
    users = query.offset(skip).limit(limit).all()
    # Populate class_name for response
    for user in users:
        if user.class_id:
            cls = db.query(models.Class).filter(models.Class.id == user.class_id).first()
            user.class_name = cls.name if cls else None
            
    return users

@router.post("/users", response_model=schemas.UserProfile)
def create_user(
    user_in: schemas.UserCreate, 
    class_id: Optional[int] = None,
    student_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin)
):
    db_user = db.query(models.User).filter(models.User.phone == user_in.phone).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Phone already registered")
        
    hashed_password = auth.get_password_hash(user_in.password)
    new_user = models.User(
        phone=user_in.phone,
        name=user_in.name,
        password_hash=hashed_password,
        role=user_in.role,
        class_id=class_id,
        student_id=student_id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    if class_id:
        cls = db.query(models.Class).filter(models.Class.id == class_id).first()
        new_user.class_name = cls.name if cls else None
        
    return new_user

@router.delete("/users/{user_id}")
def delete_user(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin)
):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user.role == "admin":
         raise HTTPException(status_code=400, detail="Cannot delete admin")
         
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted"}

@router.post("/users/{user_id}/reset-password")
def reset_password(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin)
):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Default password is '123456'
    db_user.password_hash = auth.get_password_hash("123456")
    db.commit()
    return {"message": "Password reset to 123456"}

# --- Dashboard ---

@router.get("/dashboard/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin)
):
    # 2. Pending Approvals (Health Requests + Pending Activities)
    pending_health = db.query(models.HealthRequest).filter(models.HealthRequest.status == "pending").count()
    pending_activities = db.query(models.Activity).filter(models.Activity.status == "pending_review").count()
    pending_approvals = pending_health + pending_activities
    
    # 3. Abnormal Count
    
    return {
        "pending_approvals": pending_approvals
    }

# --- Import ---

@router.post("/import/students")
async def import_students(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin)
):
    if not file.filename.endswith(('.xls', '.xlsx')):
        raise HTTPException(status_code=400, detail="无效的文件格式")
        
    contents = await file.read()
    try:
        df = pd.read_excel(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"读取Excel文件失败: {str(e)}")
        
    required_columns = ['姓名', '手机号', '密码', '学号', '所属班级名称']
    if not all(col in df.columns for col in required_columns):
        raise HTTPException(status_code=400, detail=f"缺少必需的列。需要: {required_columns}")
        
    results = {"success": 0, "failed": 0, "errors": []}
    
    for index, row in df.iterrows():
        try:
            name = str(row['姓名']).strip()
            phone = str(row['手机号']).strip()
            password = str(row['密码']).strip()
            student_id = str(row['学号']).strip()
            class_name = str(row['所属班级名称']).strip()
            
            # Check phone
            if db.query(models.User).filter(models.User.phone == phone).first():
                raise ValueError("手机号已存在")
                
            # Check class
            db_class = db.query(models.Class).filter(models.Class.name == class_name).first()
            if not db_class:
                # Create class if not exists
                db_class = models.Class(name=class_name)
                db.add(db_class)
                db.commit()
                db.refresh(db_class)
                
            hashed_password = auth.get_password_hash(password)
            new_user = models.User(
                phone=phone,
                name=name,
                password_hash=hashed_password,
                role="student",
                student_id=student_id,
                class_id=db_class.id
            )
            db.add(new_user)
            db.commit()
            results["success"] += 1
            
        except Exception as e:
            db.rollback()
            results["failed"] += 1
            results["errors"].append({"row": index + 2, "name": row.get('姓名', 'Unknown'), "error": str(e)})
            
    return results

@router.get("/import/template/students")
def get_student_template(current_user: models.User = Depends(get_current_admin)):
    df = pd.DataFrame(columns=["姓名", "手机号", "密码", "学号", "所属班级名称"])
    stream = io.BytesIO()
    with pd.ExcelWriter(stream, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    stream.seek(0)
    
    return StreamingResponse(
        stream, 
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=student_import_template.xlsx"}
    )

@router.get("/import/template/teachers")
def get_teacher_template(current_user: models.User = Depends(get_current_admin)):
    df = pd.DataFrame(columns=["姓名", "手机号", "密码", "工号"])
    stream = io.BytesIO()
    with pd.ExcelWriter(stream, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    stream.seek(0)
    
    return StreamingResponse(
        stream, 
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=teacher_import_template.xlsx"}
    )

@router.post("/import/teachers")
async def import_teachers(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin)
):
    if not file.filename.endswith(('.xls', '.xlsx')):
        raise HTTPException(status_code=400, detail="无效的文件格式")
        
    contents = await file.read()
    try:
        df = pd.read_excel(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"读取Excel文件失败: {str(e)}")
        
    required_columns = ['姓名', '手机号', '密码', '工号']
    if not all(col in df.columns for col in required_columns):
        raise HTTPException(status_code=400, detail=f"缺少必需的列。需要: {required_columns}")
        
    results = {"success": 0, "failed": 0, "errors": []}
    
    for index, row in df.iterrows():
        try:
            name = str(row['姓名']).strip()
            phone = str(row['手机号']).strip()
            password = str(row['密码']).strip()
            # '工号' might be mapped to student_id or a new field, using student_id for simplicity as generic ID
            staff_id = str(row['工号']).strip()
            
            # Check phone
            if db.query(models.User).filter(models.User.phone == phone).first():
                raise ValueError("手机号已存在")
                
            hashed_password = auth.get_password_hash(password)
            new_user = models.User(
                phone=phone,
                name=name,
                password_hash=hashed_password,
                role="teacher",
                student_id=staff_id
            )
            db.add(new_user)
            db.commit()
            results["success"] += 1
            
        except Exception as e:
            db.rollback()
            results["failed"] += 1
            results["errors"].append({"row": index + 2, "name": row.get('姓名', 'Unknown'), "error": str(e)})
            
    return results
