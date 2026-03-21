from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import pandas as pd
import io

from .database import get_db, engine
from . import models, schemas, auth

# 与主库共用，不强制建表（主 backend 已建）
try:
    models.Base.metadata.create_all(bind=engine)
except Exception:
    pass


def _sunshine_score(valid_count: int) -> int:
    """10-20-40 阶梯计分"""
    if valid_count <= 10:
        return 0
    if valid_count < 20:
        return 42 + (valid_count - 11) * 2
    if valid_count == 20:
        return 60
    return min(60 + (valid_count - 20) * 2, 100)

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
    class_name = getattr(user.student_class, "name", None) if getattr(user, "student_class", None) else None
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "user_id": user.id,
        "name": user.name,
        "class_name": class_name,
        "student_id": getattr(user, "student_id", None),
        "major": getattr(user, "major", None),
    }

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
@app.get("/admin/users/majors")
def get_user_majors(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_admin)):
    rows = (
        db.query(models.User.major)
        .filter(models.User.role == "student", models.User.major.isnot(None), models.User.major != "")
        .distinct()
        .all()
    )
    return [r[0] for r in rows if r[0]]


@app.get("/admin/users", response_model=List[schemas.UserProfile])
def get_users(
    role: Optional[str] = None,
    class_id: Optional[int] = None,
    class_name: Optional[str] = None,
    major: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_admin),
):
    query = db.query(models.User)
    if role:
        query = query.filter(models.User.role == role)
    if class_id:
        query = query.filter(models.User.class_id == class_id)
    if major:
        query = query.filter(models.User.major == major)
    if class_name:
        query = query.join(models.Class, models.User.class_id == models.Class.id).filter(models.Class.name == class_name)
    users = query.offset(skip).limit(limit).all()
    for user in users:
        if user.class_id:
            cls = db.query(models.Class).filter(models.Class.id == user.class_id).first()
            user.class_name = cls.name if cls else None
    return users


@app.post("/admin/users", response_model=schemas.UserProfile)
def create_user(
    user_in: schemas.UserCreate,
    class_id: Optional[int] = None,
    student_id: Optional[str] = None,
    major: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_admin),
):
    if db.query(models.User).filter(models.User.phone == user_in.phone).first():
        raise HTTPException(status_code=400, detail="Phone already registered")
    new_user = models.User(
        phone=user_in.phone,
        name=user_in.name,
        password_hash=auth.get_password_hash(user_in.password),
        role=user_in.role,
        class_id=class_id,
        student_id=student_id,
        major=major,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    if class_id:
        cls = db.query(models.Class).filter(models.Class.id == class_id).first()
        new_user.class_name = cls.name if cls else None
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
    if not file.filename.endswith((".xls", ".xlsx")):
        raise HTTPException(status_code=400, detail="无效的文件格式")
    contents = await file.read()
    try:
        df = pd.read_excel(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"读取Excel失败: {str(e)}")
    required = ["姓名", "手机号", "密码", "学号", "所属班级名称", "专业/课程"]
    if not all(c in df.columns for c in required):
        raise HTTPException(status_code=400, detail=f"缺少列: {required}")
    results = {"success": 0, "failed": 0, "errors": []}
    for i, row in df.iterrows():
        try:
            name = str(row["姓名"]).strip()
            phone = str(row["手机号"]).strip()
            password = str(row["密码"]).strip()
            student_id = str(row["学号"]).strip()
            class_name = str(row["所属班级名称"]).strip()
            major = str(row["专业/课程"]).strip() if pd.notna(row.get("专业/课程")) else ""
            if db.query(models.User).filter(models.User.phone == phone).first():
                raise ValueError("手机号已存在")
            cls = db.query(models.Class).filter(models.Class.name == class_name).first()
            if not cls:
                cls = models.Class(name=class_name)
                db.add(cls)
                db.commit()
                db.refresh(cls)
            db.add(models.User(
                phone=phone,
                name=name,
                password_hash=auth.get_password_hash(password),
                role="student",
                student_id=student_id,
                class_id=cls.id,
                major=major or None,
            ))
            profile = db.query(models.StudentProfile).filter(models.StudentProfile.student_id == student_id).first()
            if profile:
                profile.full_name = name
                profile.class_name = class_name
                profile.major = major or profile.major
            else:
                db.add(models.StudentProfile(
                    student_id=student_id,
                    full_name=name,
                    gender="male",
                    class_name=class_name,
                    major=major or None,
                    is_activated=False,
                ))
            db.commit()
            results["success"] += 1
        except Exception as e:
            db.rollback()
            results["failed"] += 1
            results["errors"].append({"row": i + 2, "name": row.get("姓名", ""), "error": str(e)})
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

@app.post("/admin/import/profiles")
async def import_profiles(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_admin),
):
    if not file.filename.endswith((".xls", ".xlsx")):
        raise HTTPException(status_code=400, detail="无效的文件格式")
    contents = await file.read()
    try:
        df = pd.read_excel(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"读取Excel失败: {str(e)}")
    required = ["学号", "姓名", "性别", "班级", "专业"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"缺少列: {missing}")
    results = {"success": 0, "failed": 0, "errors": []}
    for index, row in df.iterrows():
        try:
            student_id = str(row["学号"]).strip()
            full_name = str(row["姓名"]).strip()
            gender = str(row["性别"]).strip().lower()
            if gender in ("男",):
                gender = "male"
            elif gender in ("女",):
                gender = "female"
            elif gender not in ("male", "female"):
                gender = "male"
            class_name = str(row["班级"]).strip()
            major = str(row["专业"]).strip() if pd.notna(row.get("专业")) else None
            profile = db.query(models.StudentProfile).filter(models.StudentProfile.student_id == student_id).first()
            if profile:
                profile.full_name = full_name
                profile.gender = gender
                profile.class_name = class_name
                profile.major = major or profile.major
            else:
                db.add(models.StudentProfile(
                    student_id=student_id,
                    full_name=full_name,
                    gender=gender,
                    class_name=class_name,
                    major=major,
                    is_activated=False,
                ))
            db.commit()
            results["success"] += 1
        except Exception as e:
            db.rollback()
            results["failed"] += 1
            results["errors"].append({"row": index + 2, "student_id": row.get("学号"), "error": str(e)})
    return results


@app.get("/admin/import/template/profiles")
def profiles_template(current_user: models.User = Depends(auth.get_current_admin_from_query)):
    df = pd.DataFrame(columns=["学号", "姓名", "性别", "班级", "专业"])
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, index=False)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=profiles_import_template.xlsx"},
    )


@app.post("/admin/mock/student-profiles")
def mock_import_student_profiles(
    profiles: List[schemas.StudentProfileCreate],
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_admin),
):
    success = failed = 0
    errors = []
    for item in profiles:
        try:
            profile = db.query(models.StudentProfile).filter(models.StudentProfile.student_id == item.student_id).first()
            if profile:
                profile.full_name = item.full_name
                profile.gender = item.gender
                profile.class_name = item.class_name
                profile.major = getattr(item, "major", None) or profile.major
            else:
                db.add(models.StudentProfile(
                    student_id=item.student_id,
                    full_name=item.full_name,
                    gender=item.gender,
                    class_name=item.class_name,
                    major=getattr(item, "major", None),
                    is_activated=False,
                ))
            db.commit()
            success += 1
        except Exception as e:
            db.rollback()
            failed += 1
            errors.append({"student_id": item.student_id, "error": str(e)})
    return {"success": success, "failed": failed, "errors": errors}


@app.get("/admin/teacher-classes/{teacher_id}")
def get_teacher_classes(teacher_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_admin)):
    items = db.query(models.TeacherClass).filter(models.TeacherClass.teacher_id == teacher_id).all()
    return [{"class_name": i.class_name} for i in items]


@app.post("/admin/teacher-classes/{teacher_id}")
def update_teacher_classes(
    teacher_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_admin),
):
    class_names = payload.get("class_names") or []
    db.query(models.TeacherClass).filter(models.TeacherClass.teacher_id == teacher_id).delete()
    for name in class_names:
        if name:
            db.add(models.TeacherClass(teacher_id=teacher_id, class_name=name))
    db.commit()
    return {"teacher_id": teacher_id, "class_names": class_names}


@app.get("/admin/sunshine/class-stats")
def get_sunshine_class_stats(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_admin)):
    classes = db.query(models.Class).all()
    class_stats = []
    for cls in classes:
        students = db.query(models.User).filter(models.User.class_id == cls.id, models.User.role == "student").all()
        total_count = len(students)
        total_valid_runs = 0
        scores = []
        passed_20_count = 0
        for u in students:
            valid_count = (
                db.query(models.Activity)
                .filter(models.Activity.user_id == u.id, models.Activity.type == "run", models.Activity.is_valid.is_(True))
                .count()
            )
            total_valid_runs += valid_count
            scores.append(_sunshine_score(valid_count))
            if valid_count >= 20:
                passed_20_count += 1
        avg_score = round(sum(scores) / len(scores), 2) if scores else 0
        pass_rate = round((passed_20_count / total_count) * 100, 1) if total_count else 0
        class_stats.append({
            "class_id": cls.id,
            "class_name": cls.name,
            "total_count": total_count,
            "total_valid_runs": total_valid_runs,
            "avg_score": avg_score,
            "pass_rate": pass_rate,
            "passed_20_count": passed_20_count,
        })
    majors_q = (
        db.query(models.User.major)
        .filter(models.User.role == "student", models.User.major.isnot(None), models.User.major != "")
        .distinct()
        .all()
    )
    major_activity = []
    for (major,) in majors_q:
        if not major:
            continue
        users_in_major = db.query(models.User).filter(models.User.role == "student", models.User.major == major).all()
        total_valid = sum(
            db.query(models.Activity)
            .filter(models.Activity.user_id == u.id, models.Activity.type == "run", models.Activity.is_valid.is_(True))
            .count()
            for u in users_in_major
        )
        major_activity.append({"major": major, "valid_runs": total_valid})
    return {"class_stats": class_stats, "major_activity": major_activity}


@app.get("/admin/import/template/students")
def student_template(current_user: models.User = Depends(auth.get_current_admin_from_query)):
    df = pd.DataFrame(columns=["姓名", "手机号", "密码", "学号", "所属班级名称", "专业/课程"])
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, index=False)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=student_import_template.xlsx"},
    )

@app.get("/admin/import/template/teachers")
def teacher_template(current_user: models.User = Depends(auth.get_current_admin_from_query)):
    df = pd.DataFrame(columns=["姓名", "手机号", "密码", "工号"])
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as w: df.to_excel(w, index=False)
    buf.seek(0)
    return StreamingResponse(buf, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=teacher_template.xlsx"})
