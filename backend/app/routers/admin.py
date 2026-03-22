
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import pandas as pd
import io

from ..database import get_db
from .. import models, schemas, auth
from ..services.score_service import calculate_total_score

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

@router.get("/users/majors")
def get_user_majors(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    """获取全校专业列表，用于账号管理页筛选下拉"""
    rows = (
        db.query(models.User.major)
        .filter(models.User.role == "student", models.User.major.isnot(None), models.User.major != "")
        .distinct()
        .all()
    )
    return [r[0] for r in rows if r[0]]


@router.get("/users", response_model=List[schemas.UserProfile])
def get_users(
    role: Optional[str] = None,
    class_id: Optional[int] = None,
    class_name: Optional[str] = None,
    major: Optional[str] = None,
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
    if major:
        query = query.filter(models.User.major == major)
    if class_name:
        query = query.join(models.Class, models.User.class_id == models.Class.id).filter(
            models.Class.name == class_name
        )

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
    # 1. Total counts
    total_students = db.query(func.count(models.User.id)).filter(models.User.role == "student").scalar() or 0
    total_teachers = db.query(func.count(models.User.id)).filter(models.User.role == "teacher").scalar() or 0
    total_classes = db.query(func.count(models.Class.id)).scalar() or 0

    # 2. Pending Approvals (Health Requests + Pending Activities)
    pending_health = db.query(models.HealthRequest).filter(models.HealthRequest.status == "pending").count()
    pending_activities = db.query(models.Activity).filter(models.Activity.status == "pending_review").count()
    pending_approvals = pending_health + pending_activities
    
    return {
        "total_students": total_students,
        "total_teachers": total_teachers,
        "total_classes": total_classes,
        "pending_approvals": pending_approvals,
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
        
    required_columns = ['姓名', '手机号', '密码', '学号', '所属班级名称', '专业/课程']
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
            major = str(row['专业/课程']).strip() if '专业/课程' in df.columns else ''
            
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
                class_id=db_class.id,
                major=major
            )
            db.add(new_user)
            # 同步/创建学生档案
            profile = db.query(models.StudentProfile).filter(
                models.StudentProfile.student_id == student_id
            ).first()
            if profile:
                profile.full_name = name
                profile.class_name = class_name
                # 如果导入表中未指定性别，则保留原有值
                if not profile.gender:
                    profile.gender = "male"
                profile.major = major or profile.major
            else:
                profile = models.StudentProfile(
                    student_id=student_id,
                    full_name=name,
                    gender="male",  # 默认值，后续可在档案中单独维护
                    class_name=class_name,
                    major=major,
                    is_activated=False,
                )
                db.add(profile)

            db.commit()
            results["success"] += 1
            
        except Exception as e:
            db.rollback()
            results["failed"] += 1
            results["errors"].append({"row": index + 2, "name": row.get('姓名', 'Unknown'), "error": str(e)})
            
    return results

@router.post("/import/profiles")
async def import_profiles(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    """
    仅导入学生档案（StudentProfile），不创建用户。
    Excel 列：学号、姓名、性别、班级、专业
    用于“档案激活”注册流程：学生需先有档案再注册。
    """
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
            if gender not in ("male", "female", "男", "女"):
                gender = "male"
            if gender == "男":
                gender = "male"
            if gender == "女":
                gender = "female"
            class_name = str(row["班级"]).strip()
            major = str(row["专业"]).strip() if pd.notna(row.get("专业")) else None

            profile = (
                db.query(models.StudentProfile)
                .filter(models.StudentProfile.student_id == student_id)
                .first()
            )
            if profile:
                profile.full_name = full_name
                profile.gender = gender
                profile.class_name = class_name
                profile.major = major or profile.major
            else:
                profile = models.StudentProfile(
                    student_id=student_id,
                    full_name=full_name,
                    gender=gender,
                    class_name=class_name,
                    major=major,
                    is_activated=False,
                )
                db.add(profile)
            db.commit()
            results["success"] += 1
        except Exception as e:
            db.rollback()
            results["failed"] += 1
            results["errors"].append(
                {"row": index + 2, "student_id": row.get("学号"), "error": str(e)}
            )

    return results


@router.get("/import/template/profiles")
def get_profiles_template(current_user: models.User = Depends(get_current_admin)):
    """下载档案导入模板（学号、姓名、性别、班级、专业）"""
    df = pd.DataFrame(columns=["学号", "姓名", "性别", "班级", "专业"])
    stream = io.BytesIO()
    with pd.ExcelWriter(stream, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    stream.seek(0)
    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=profiles_import_template.xlsx"},
    )


@router.get("/import/template/students")
def get_student_template(current_user: models.User = Depends(get_current_admin)):
    df = pd.DataFrame(columns=["姓名", "手机号", "密码", "学号", "所属班级名称", "专业/课程"])
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


@router.post("/mock/student-profiles")
def mock_import_student_profiles(
    profiles: List[schemas.StudentProfileCreate],
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    """
    管理端 Mock 接口：批量导入学生档案(StudentProfile)，用于测试“档案激活”注册流程。

    请求体示例:
    [
      {"student_id": "2024001", "full_name": "张三", "gender": "male", "class_name": "22级3班"},
      {"student_id": "2024002", "full_name": "李四", "gender": "female", "class_name": "22级3班"}
    ]
    """
    success = 0
    failed = 0
    errors: list[dict] = []

    for item in profiles:
        try:
            profile = (
                db.query(models.StudentProfile)
                .filter(models.StudentProfile.student_id == item.student_id)
                .first()
            )
            if profile:
                # 更新基础信息，但不重置 is_activated 状态，防止误覆盖
                profile.full_name = item.full_name
                profile.gender = item.gender
                profile.class_name = item.class_name
                if getattr(item, "major", None) is not None:
                    profile.major = item.major
            else:
                profile = models.StudentProfile(
                    student_id=item.student_id,
                    full_name=item.full_name,
                    gender=item.gender,
                    class_name=item.class_name,
                    major=getattr(item, "major", None),
                    is_activated=False,
                )
                db.add(profile)
            success += 1
        except Exception as e:
            db.rollback()
            failed += 1
            errors.append(
                {
                    "student_id": item.student_id,
                    "full_name": item.full_name,
                    "error": str(e),
                }
            )
        else:
            db.commit()

    return {
        "success": success,
        "failed": failed,
        "errors": errors,
    }


@router.get("/teacher-classes/{teacher_id}")
def get_teacher_classes(
    teacher_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    """获取指定教师当前绑定的班级列表。"""
    items = (
        db.query(models.TeacherClass)
        .filter(models.TeacherClass.teacher_id == teacher_id)
        .all()
    )
    return [{"class_name": i.class_name} for i in items]


# --- 阳光跑全校看板（班级统计）---

@router.get("/sunshine/class-stats")
def get_sunshine_class_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    """
    按班级聚合：总人数、总有效跑步次数、班级平均分（10-20-40 阶梯）。
    班级达标率：达到 20 次及格线的人数占比。
    专业活跃度：按专业汇总有效跑步次数（用于饼图）。
    """
    classes = db.query(models.Class).all()
    class_stats = []
    for cls in classes:
        students = (
            db.query(models.User)
            .filter(models.User.class_id == cls.id, models.User.role == "student")
            .all()
        )
        total_count = len(students)
        total_valid_runs = 0
        scores = []
        passed_20_count = 0  # 达标 20 次及格线人数
        for u in students:
            valid_count = (
                db.query(models.Activity)
                .filter(
                    models.Activity.user_id == u.id,
                    models.Activity.type == "run",
                    models.Activity.is_valid.is_(True),
                )
                .count()
            )
            total_valid_runs += valid_count
            scores.append(calculate_total_score(valid_count))
            if valid_count >= 20:
                passed_20_count += 1
        avg_score = round(sum(scores) / len(scores), 2) if scores else 0
        pass_rate = round((passed_20_count / total_count) * 100, 1) if total_count else 0
        class_stats.append(
            {
                "class_id": cls.id,
                "class_name": cls.name,
                "total_count": total_count,
                "total_valid_runs": total_valid_runs,
                "avg_score": avg_score,
                "pass_rate": pass_rate,
                "passed_20_count": passed_20_count,
            }
        )
    # 专业活跃度：按 User.major 汇总有效跑步次数
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
        users_in_major = (
            db.query(models.User)
            .filter(models.User.role == "student", models.User.major == major)
            .all()
        )
        total_valid = 0
        for u in users_in_major:
            total_valid += (
                db.query(models.Activity)
                .filter(
                    models.Activity.user_id == u.id,
                    models.Activity.type == "run",
                    models.Activity.is_valid.is_(True),
                )
                .count()
            )
        major_activity.append({"major": major, "valid_runs": total_valid})
    return {
        "class_stats": class_stats,
        "major_activity": major_activity,
    }


@router.post("/teacher-classes/{teacher_id}")
def update_teacher_classes(
    teacher_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    """
    更新教师与班级的绑定关系。
    请求体示例：{"class_names": ["22级3班", "22级4班"] }
    """
    class_names = payload.get("class_names") or []
    # 清空原有绑定
    db.query(models.TeacherClass).filter(
        models.TeacherClass.teacher_id == teacher_id
    ).delete()

    # 新建绑定
    for name in class_names:
        if not name:
            continue
        db.add(models.TeacherClass(teacher_id=teacher_id, class_name=name))

    db.commit()
    return {"teacher_id": teacher_id, "class_names": class_names}
