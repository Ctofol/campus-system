
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List, Optional, Any
import numbers
import math
import pandas as pd
import io

from ..database import get_db
from .. import models, schemas, auth
from ..services.score_service import calculate_total_score

router = APIRouter(
    prefix="/manage",
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


DEFAULT_SUBJECT_NAMES = ["篮球", "羽毛球", "乒乓球", "游泳", "网球", "跆拳道"]


def ensure_default_subject_options(db: Session) -> None:
    """首次访问时写入默认选科，与教师端、模拟种子常用项对齐。"""
    if db.query(models.SubjectOption).first() is not None:
        return
    for i, n in enumerate(DEFAULT_SUBJECT_NAMES):
        db.add(models.SubjectOption(name=n, sort_order=i))
    db.commit()


def normalize_teacher_subject_names(db: Session, names: Any) -> List[str]:
    """教师绑定选科须来自选科库。"""
    ensure_default_subject_options(db)
    allowed = {s.name for s in db.query(models.SubjectOption).all()}
    out: List[str] = []
    invalid: List[str] = []
    for raw in names or []:
        n = (str(raw) if raw is not None else "").strip()
        if not n:
            continue
        if n not in allowed:
            invalid.append(n)
        else:
            out.append(n)
    if invalid:
        raise HTTPException(
            status_code=400,
            detail="以下选科不在选科库中，请先在「选科管理」添加：" + "、".join(invalid),
        )
    return out


# --- Classes Management ---

@router.get("/classes", response_model=List[schemas.ClassOut])
def get_classes(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin)
):
    classes = (
        db.query(models.Class)
        .options(joinedload(models.Class.teacher), joinedload(models.Class.major))
        .offset(skip)
        .limit(limit)
        .all()
    )
    for cls in classes:
        cls.student_count = db.query(func.count(models.User.id)).filter(models.User.class_id == cls.id).scalar()
        cls.teacher_name = cls.teacher.name if cls.teacher else None
    return classes


def _assert_teacher_id(db: Session, teacher_id: Optional[int]) -> None:
    if teacher_id is None:
        return
    t = (
        db.query(models.User)
        .filter(models.User.id == teacher_id, models.User.role == "teacher")
        .first()
    )
    if not t:
        raise HTTPException(status_code=400, detail="无效的教师账号，请选择角色为教师的用户")


@router.post("/classes", response_model=schemas.ClassOut)
def create_class(
    class_in: schemas.ClassCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin)
):
    db_class = db.query(models.Class).filter(models.Class.name == class_in.name).first()
    if db_class:
        raise HTTPException(status_code=400, detail="Class already exists")

    _assert_teacher_id(db, class_in.teacher_id)
    new_class = models.Class(
        name=class_in.name,
        teacher_id=class_in.teacher_id,
        major_id=class_in.major_id,
    )
    db.add(new_class)
    db.commit()
    db.refresh(new_class)
    new_class = (
        db.query(models.Class)
        .options(joinedload(models.Class.teacher), joinedload(models.Class.major))
        .filter(models.Class.id == new_class.id)
        .first()
    )
    new_class.student_count = 0
    new_class.teacher_name = new_class.teacher.name if new_class.teacher else None
    return new_class


@router.patch("/classes/{class_id}", response_model=schemas.ClassOut)
def update_class_teacher(
    class_id: int,
    body: schemas.ClassTeacherUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    """设置或解除班级绑定教师（Class.teacher_id，用于教师端按班级管辖学生）。"""
    db_class = db.query(models.Class).filter(models.Class.id == class_id).first()
    if not db_class:
        raise HTTPException(status_code=404, detail="Class not found")
    _assert_teacher_id(db, body.teacher_id)
    db_class.teacher_id = body.teacher_id
    db.commit()
    db.refresh(db_class)
    db_class = (
        db.query(models.Class)
        .options(joinedload(models.Class.teacher), joinedload(models.Class.major))
        .filter(models.Class.id == class_id)
        .first()
    )
    db_class.student_count = db.query(func.count(models.User.id)).filter(models.User.class_id == db_class.id).scalar()
    db_class.teacher_name = db_class.teacher.name if db_class.teacher else None
    return db_class

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
        db.query(models.Major.name)
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
        # 使用关联查询进行专业过滤
        query = query.join(models.Major, models.User.major_id == models.Major.id).filter(
            models.Major.name == major
        )
    if class_name:
        query = query.join(models.Class, models.User.class_id == models.Class.id).filter(
            models.Class.name == class_name
        )

    users = query.offset(skip).limit(limit).all()
    # 属性字段（major, class_name）已通过 models.py 的 @property 自动处理
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
        student_id=student_id,
    )
    db.add(new_user)
    db.flush()
    if class_id:
        cls = db.query(models.Class).filter(models.Class.id == class_id).first()
        if cls and cls.major_id is not None:
            new_user.major_id = cls.major_id
            mj = db.query(models.Major).filter(models.Major.id == cls.major_id).first()
            if mj:
                new_user.major_name = mj.name
    db.commit()
    db.refresh(new_user)

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


def _admin_activity_record_kind(act: models.Activity) -> str:
    if act.type == "test":
        return "体测"
    if act.task_id:
        return "任务跑步"
    if act.type == "run" and (act.source == "free" or act.source is None):
        return "阳光跑"
    return "跑步"


@router.get("/users/{user_id}/activities", response_model=schemas.AdminStudentActivitiesPage)
def admin_student_activities(
    user_id: int,
    page: int = 1,
    size: int = 20,
    activity_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    """管理端：按学生查看运动记录（阳光跑 / 任务跑 / 体测）"""
    stu = (
        db.query(models.User)
        .filter(models.User.id == user_id, models.User.role == "student")
        .first()
    )
    if not stu:
        raise HTTPException(status_code=404, detail="学生不存在")

    q = (
        db.query(models.Activity)
        .options(joinedload(models.Activity.metrics), joinedload(models.Activity.task))
        .filter(models.Activity.user_id == user_id)
    )
    if activity_type in ("run", "test"):
        q = q.filter(models.Activity.type == activity_type)

    total = q.count()
    rows = (
        q.order_by(models.Activity.started_at.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    items: List[schemas.AdminStudentActivityItem] = []
    for act in rows:
        m = act.metrics
        items.append(
            schemas.AdminStudentActivityItem(
                id=act.id,
                type=act.type,
                record_kind=_admin_activity_record_kind(act),
                source=act.source,
                started_at=act.started_at,
                ended_at=act.ended_at,
                is_valid=bool(act.is_valid),
                fail_reason=act.fail_reason,
                distance_km=m.distance if m else None,
                duration_sec=m.duration if m else None,
                pace=str(m.pace) if m and m.pace is not None else None,
                task_id=act.task_id,
                task_title=act.task.title if act.task else None,
            )
        )
    return schemas.AdminStudentActivitiesPage(
        items=items, total=total, page=page, size=size
    )


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

_STUDENT_IMPORT_HEADER_ALIASES = {
    "属班级名称": "所属班级名称",
    "所属班级名": "所属班级名称",
    "属班级名": "所属班级名称",
    "班级名称": "所属班级名称",
    "班级": "所属班级名称",
}


def _normalize_student_import_df_columns(df: pd.DataFrame) -> pd.DataFrame:
    """表头去空白、全角斜杠；兼容常见少字/别名列名。"""
    rename = {}
    for c in df.columns:
        key = str(c).strip().replace("\u3000", " ").replace("／", "/")
        key = _STUDENT_IMPORT_HEADER_ALIASES.get(key, key)
        rename[c] = key
    return df.rename(columns=rename)


def _excel_cell_str(val: Any) -> str:
    """把 Excel 单元格统一成干净字符串（避免手机号/学号变成 1.38e+11、xxx.0）。"""
    if val is None:
        return ""
    if isinstance(val, str):
        s = val.strip()
        if s.lower() in ("nan", "none", "<na>", "nat"):
            return ""
        if len(s) > 2 and s[-2:] == ".0" and s[:-2].isdigit():
            return s[:-2]
        return s
    try:
        if pd.isna(val):
            return ""
    except TypeError:
        pass
    if isinstance(val, bool):
        return str(val)
    if isinstance(val, numbers.Integral):
        return str(int(val))
    if isinstance(val, float):
        if math.isnan(val):
            return ""
        r = round(val)
        if abs(val - r) < 1e-9:
            return str(int(r))
        return str(val).strip()
    s = str(val).strip()
    if s.lower() in ("nan", "none", "<na>"):
        return ""
    if len(s) > 2 and s[-2:] == ".0" and s[:-2].replace(".", "", 1).isdigit():
        return s[:-2]
    return s


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

    df = _normalize_student_import_df_columns(df)
    required_columns = ['姓名', '手机号', '密码', '学号', '所属班级名称', '专业/课程']
    if not all(col in df.columns for col in required_columns):
        raise HTTPException(
            status_code=400,
            detail=f"缺少必需的列。需要: {required_columns}；当前列: {list(df.columns)}",
        )
        
    results = {"success": 0, "failed": 0, "errors": []}
    
    for index, row in df.iterrows():
        try:
            name = _excel_cell_str(row.get("姓名"))
            phone = _excel_cell_str(row.get("手机号"))
            password = _excel_cell_str(row.get("密码"))
            student_id = _excel_cell_str(row.get("学号"))
            class_name = _excel_cell_str(row.get("所属班级名称"))
            major = _excel_cell_str(row.get("专业/课程"))

            if not name:
                raise ValueError("姓名为空")
            if not phone:
                raise ValueError("手机号为空")
            if not password:
                raise ValueError("密码为空")
            if not student_id:
                raise ValueError("学号为空（若为科学计数请在 Excel 中将该列设为「文本」后重填）")
            if not class_name:
                raise ValueError("所属班级名称为空")
            if not major:
                raise ValueError("专业/课程为空")

            if db.query(models.User).filter(models.User.phone == phone).first():
                raise ValueError("手机号已存在")
            if db.query(models.User).filter(models.User.student_id == student_id).first():
                raise ValueError("学号已存在对应账号")

            # 1. 找到或创建专业 (Major)
            db_major = db.query(models.Major).filter(models.Major.name == major).first()
            if not db_major:
                db_major = models.Major(name=major)
                db.add(db_major)
                db.flush()
                
            # 2. 找到或创建班级 (Class) - 绑定到专业
            db_class = db.query(models.Class).filter(
                models.Class.name == class_name, 
                models.Class.major_id == db_major.id
            ).first()
            if not db_class:
                db_class = models.Class(name=class_name, major_id=db_major.id)
                db.add(db_class)
                db.flush()

            # 3. 必须先有档案再建用户（users.student_id 外键 -> student_profiles）
            profile = db.query(models.StudentProfile).filter(
                models.StudentProfile.student_id == student_id
            ).first()
            if profile:
                profile.full_name = name
                profile.class_name = class_name
                if not profile.gender:
                    profile.gender = "male"
                profile.major = major or profile.major
            else:
                profile = models.StudentProfile(
                    student_id=student_id,
                    full_name=name,
                    gender="male",
                    class_name=class_name,
                    major=major,
                    is_activated=False,
                )
                db.add(profile)
            db.flush()

            hashed_password = auth.get_password_hash(password)
            new_user = models.User(
                phone=phone,
                name=name,
                password_hash=hashed_password,
                role="student",
                student_id=student_id,
                class_id=db_class.id,
                major_id=db_major.id,
                major_name=major,
            )
            db.add(new_user)
            profile.is_activated = True

            db.commit()
            results["success"] += 1
            
        except Exception as e:
            db.rollback()
            results["failed"] += 1
            results["errors"].append({"row": int(index) + 2, "name": row.get("姓名", "Unknown"), "error": str(e)})
            
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
            subject = None
            if "选科" in df.columns and pd.notna(row.get("选科")):
                subject = str(row.get("选科", "")).strip() or None

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
                profile.subject = subject or profile.subject
            else:
                profile = models.StudentProfile(
                    student_id=student_id,
                    full_name=full_name,
                    gender=gender,
                    class_name=class_name,
                    major=major,
                    subject=subject,
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
    """下载档案导入模板（选科可选）"""
    df = pd.DataFrame(columns=["学号", "姓名", "性别", "班级", "专业", "选科"])
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


# --- 体育选科库（管理端维护，教师「分配管辖选科」多选框数据源）---

@router.get("/subjects", response_model=List[schemas.SubjectOptionOut])
def list_subject_options(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    ensure_default_subject_options(db)
    return (
        db.query(models.SubjectOption)
        .order_by(models.SubjectOption.sort_order, models.SubjectOption.id)
        .all()
    )


@router.post("/subjects", response_model=schemas.SubjectOptionOut)
def create_subject_option(
    body: schemas.SubjectOptionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    ensure_default_subject_options(db)
    name = (body.name or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="选科名称不能为空")
    exists = db.query(models.SubjectOption).filter(models.SubjectOption.name == name).first()
    if exists:
        raise HTTPException(status_code=400, detail="该选科已存在")
    max_order = db.query(func.max(models.SubjectOption.sort_order)).scalar()
    next_order = (max_order if max_order is not None else -1) + 1
    row = models.SubjectOption(name=name, sort_order=next_order)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.delete("/subjects/{subject_id}")
def delete_subject_option(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    opt = db.query(models.SubjectOption).filter(models.SubjectOption.id == subject_id).first()
    if not opt:
        raise HTTPException(status_code=404, detail="选科不存在")
    db.query(models.TeacherSubject).filter(
        models.TeacherSubject.subject_name == opt.name
    ).delete(synchronize_session=False)
    db.delete(opt)
    db.commit()
    return {"ok": True}


@router.get("/teacher-subjects/{teacher_id}")
def get_teacher_classes(
    teacher_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    """获取指定教师当前绑定的选科列表。"""
    items = (
        db.query(models.TeacherSubject)
        .filter(models.TeacherSubject.teacher_id == teacher_id)
        .all()
    )
    return [{"name": i.subject_name} for i in items]


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
                "class_name": f"{cls.major.name if cls.major else ''} {cls.name}",
                "total_count": total_count,
                "total_valid_runs": total_valid_runs,
                "avg_score": avg_score,
                "pass_rate": pass_rate,
                "passed_20_count": passed_20_count,
            }
        )
    # 专业活跃度：按「行政班所属专业」汇总有效跑步次数（与 user.major_id 解耦，避免大量学生 major_id 为空时饼图全为 0）
    majors_objs = db.query(models.Major).all()
    major_activity = []
    for m_obj in majors_objs:
        users_in_major = (
            db.query(models.User)
            .join(models.Class, models.Class.id == models.User.class_id)
            .filter(
                models.User.role == "student",
                models.Class.major_id == m_obj.id,
            )
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
        major_activity.append({"major": m_obj.name, "valid_runs": total_valid})
    return {
        "class_stats": class_stats,
        "major_activity": major_activity,
    }


@router.post("/teacher-subjects/{teacher_id}")
def update_teacher_subjects(
    teacher_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    """
    更新教师与选科的绑定关系。
    请求体示例：{"subject_names": ["篮球", "羽毛球"] }
    """
    subject_names = normalize_teacher_subject_names(db, payload.get("subject_names"))
    # 清空原有绑定
    db.query(models.TeacherSubject).filter(
        models.TeacherSubject.teacher_id == teacher_id
    ).delete()

    # 新建绑定
    for name in subject_names:
        if not name:
            continue
        db.add(models.TeacherSubject(teacher_id=teacher_id, subject_name=name))

    db.commit()
    return {"teacher_id": teacher_id, "subject_names": subject_names}


def _require_teacher_user(db: Session, teacher_id: int) -> models.User:
    u = db.query(models.User).filter(models.User.id == teacher_id).first()
    if not u or u.role != "teacher":
        raise HTTPException(status_code=404, detail="教师不存在或不是教师角色")
    return u


@router.get("/teachers/{teacher_id}/bound-students", response_model=List[schemas.UserProfile])
def list_teacher_bound_students(
    teacher_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    """管理员查看某教师显式绑定的学员（并入教师端管辖学生列表）。"""
    _require_teacher_user(db, teacher_id)
    ids = [
        r[0]
        for r in db.query(models.TeacherStudent.student_user_id)
        .filter(models.TeacherStudent.teacher_id == teacher_id)
        .all()
    ]
    if not ids:
        return []
    users = (
        db.query(models.User)
        .filter(models.User.id.in_(ids), models.User.role == "student")
        .order_by(models.User.id)
        .all()
    )
    return users


@router.post("/teachers/{teacher_id}/bound-students")
def add_teacher_bound_students(
    teacher_id: int,
    body: schemas.TeacherBoundStudentsAdd,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    """为教师追加绑定学员（幂等跳过已绑定）。"""
    _require_teacher_user(db, teacher_id)
    added = 0
    for sid in body.student_user_ids or []:
        if not sid:
            continue
        stu = (
            db.query(models.User)
            .filter(models.User.id == sid, models.User.role == "student")
            .first()
        )
        if not stu:
            raise HTTPException(status_code=400, detail=f"无效的学生用户 id: {sid}")
        if stu.id == teacher_id:
            raise HTTPException(status_code=400, detail="不能绑定教师本人为用户 id")
        exists = (
            db.query(models.TeacherStudent)
            .filter(
                models.TeacherStudent.teacher_id == teacher_id,
                models.TeacherStudent.student_user_id == sid,
            )
            .first()
        )
        if exists:
            continue
        db.add(
            models.TeacherStudent(teacher_id=teacher_id, student_user_id=sid)
        )
        added += 1
    db.commit()
    return {"teacher_id": teacher_id, "added": added}


@router.delete("/teachers/{teacher_id}/bound-students/{student_user_id}")
def remove_teacher_bound_student(
    teacher_id: int,
    student_user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    """解除教师与某学员的显式绑定。"""
    _require_teacher_user(db, teacher_id)
    row = (
        db.query(models.TeacherStudent)
        .filter(
            models.TeacherStudent.teacher_id == teacher_id,
            models.TeacherStudent.student_user_id == student_user_id,
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="未找到该绑定关系")
    db.delete(row)
    db.commit()
    return {"ok": True}
