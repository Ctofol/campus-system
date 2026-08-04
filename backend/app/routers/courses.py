"""
Course Management Router (Phase 4.2 Enhanced)
课程管理路由 - 完整的CRUD + 选课 + 进度管理
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from .. import models, schemas, auth
from ..database import get_db
from ..services.audit_service import record_audit
from ..services.teacher_service import get_managed_students_query

router = APIRouter(prefix="/courses", tags=["courses"])


async def _optional_user(token: Optional[str], db: Session) -> Optional[models.User]:
    if not token:
        return None
    try:
        return await auth.get_current_user(token, db)
    except HTTPException:
        return None


def _active_enrollment(db: Session, user_id: int, course_id: int):
    return db.query(models.Enrollment).filter(
        models.Enrollment.student_id == user_id,
        models.Enrollment.course_id == course_id,
        models.Enrollment.status == "active",
    ).first()


def _may_view_course(course: models.Course, user: Optional[models.User], db: Session) -> bool:
    if course.lifecycle_status == "archived":
        if not user:
            return False
        if user.role == "admin" or (user.role == "teacher" and course.teacher_id == user.id):
            return True
        return user.role == "student" and _active_enrollment(db, user.id, course.id) is not None
    if course.is_public:
        return True
    if not user:
        return False
    if user.role == "admin":
        return True
    if user.role == "teacher" and course.teacher_id == user.id:
        return True
    return user.role == "student" and _active_enrollment(db, user.id, course.id) is not None


def _require_course_access(course: models.Course, user: Optional[models.User], db: Session) -> None:
    if not _may_view_course(course, user, db):
        raise HTTPException(status_code=403, detail="该课程未公开或你尚未获得学习权限")


def _require_student_enrollment(course: models.Course, user: models.User, db: Session) -> None:
    if user.role != "student":
        raise HTTPException(status_code=403, detail="仅学生可记录课程学习进度")
    if _active_enrollment(db, user.id, course.id) is None:
        raise HTTPException(status_code=403, detail="请先选课后再学习和记录进度")


def _require_course_owner(course: models.Course, user: models.User) -> None:
    if course.teacher_id != user.id:
        raise HTTPException(status_code=403, detail="只能管理自己创建的课程")


def _build_course_list_item(
    course: models.Course,
    db: Session,
    current_user: Optional[models.User],
) -> dict:
    """列表项：选课状态、进度、课时、讲师等（供课程学习页卡片展示）"""
    contents = (
        db.query(models.CourseContent)
        .filter(models.CourseContent.course_id == course.id)
        .order_by(models.CourseContent.order)
        .all()
    )
    lesson_total = len(contents)
    duration_minutes = sum((c.duration or 0) for c in contents) // 60

    teacher_name = None
    if course.teacher_id:
        teacher = course.teacher or db.query(models.User).filter(
            models.User.id == course.teacher_id
        ).first()
        if teacher and teacher.name and str(teacher.name).strip():
            teacher_name = str(teacher.name).strip()

    enrolled = False
    progress_percent = 0
    lesson_completed = 0
    if current_user and current_user.role == "student":
        enrollment = db.query(models.Enrollment).filter(
            models.Enrollment.student_id == current_user.id,
            models.Enrollment.course_id == course.id,
            models.Enrollment.status == "active",
        ).first()
        enrolled = enrollment is not None
        if enrolled and contents:
            content_ids = [c.id for c in contents]
            progress_records = db.query(models.CourseProgress).filter(
                models.CourseProgress.student_id == current_user.id,
                models.CourseProgress.content_id.in_(content_ids),
            ).all()
            lesson_completed = sum(1 for p in progress_records if p.completed)
            if progress_records:
                total_progress = sum(float(p.progress or 0) for p in progress_records)
                progress_percent = int(total_progress / len(contents))
            progress_percent = max(0, min(100, progress_percent))

    enrollment_count = db.query(models.Enrollment).filter(
        models.Enrollment.course_id == course.id,
        models.Enrollment.status == "active",
    ).count()

    return {
        "id": course.id,
        "title": course.title,
        "description": course.description,
        "cover_url": course.cover_url,
        "category": course.category,
        "is_public": course.is_public,
        "teacher_id": course.teacher_id,
        "created_at": course.created_at,
        "enrollment_count": enrollment_count,
        "enrolled": enrolled,
        "teacher_name": teacher_name,
        "lesson_total": lesson_total,
        "lesson_completed": lesson_completed,
        "progress_percent": progress_percent,
        "duration_minutes": duration_minutes,
    }


# ==================== 课程 CRUD ====================

@router.post("/", response_model=schemas.CourseOut)
async def create_course(
    course_in: schemas.CourseCreate,
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    """创建课程（仅教师）"""
    new_course = models.Course(
        **course_in.dict(),
        teacher_id=current_user.id
    )
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course


@router.put("/{course_id}", response_model=schemas.CourseOut)
async def update_course(
    course_id: int,
    course_in: schemas.CourseCreate,
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    """更新课程基础信息（仅教师）"""
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # 检查权限：只有课程创建者可以修改
    if course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this course")
    
    # 更新字段
    for key, value in course_in.dict().items():
        setattr(course, key, value)
    
    course.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(course)
    return course


@router.delete("/{course_id}")
async def delete_course(
    course_id: int,
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    """归档课程（兼容原删除接口，仅教师）。"""
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # 检查权限
    if course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this course")
    
    if course.lifecycle_status == "archived":
        return {"success": True, "archived": True}
    course.lifecycle_status = "archived"
    course.archived_at = datetime.utcnow()
    record_audit(
        db,
        actor=current_user,
        action="course.archive",
        resource_type="course",
        resource_id=course.id,
        detail={
            "enrollments": db.query(models.Enrollment).filter(models.Enrollment.course_id == course.id).count(),
            "contents": db.query(models.CourseContent).filter(models.CourseContent.course_id == course.id).count(),
        },
    )
    db.commit()
    
    return {"success": True, "archived": True}


@router.get("/", response_model=schemas.CourseListResponse)
async def get_courses(
    page: int = 1,
    size: int = 20,
    category: Optional[str] = None,
    teacher_id: Optional[int] = None,
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(auth.oauth2_scheme)
):
    """获取课程列表（无需登录）"""
    current_user = await _optional_user(token, db)
    
    query = db.query(models.Course)
    query = query.filter(models.Course.lifecycle_status != "archived")
    
    if current_user is None:
        query = query.filter(models.Course.is_public.is_(True))
    elif current_user.role == "student":
        enrolled_ids = db.query(models.Enrollment.course_id).filter(
            models.Enrollment.student_id == current_user.id,
            models.Enrollment.status == "active",
        )
        query = query.filter(or_(models.Course.is_public.is_(True), models.Course.id.in_(enrolled_ids)))
    elif current_user.role == "teacher":
        query = query.filter(or_(models.Course.is_public.is_(True), models.Course.teacher_id == current_user.id))
    
    # 按分类筛选
    if category:
        query = query.filter(models.Course.category == category)
    
    # 按教师筛选
    if teacher_id:
        query = query.filter(models.Course.teacher_id == teacher_id)
    
    total = query.count()
    courses = query.order_by(models.Course.created_at.desc()).offset((page - 1) * size).limit(size).all()
    
    items = [
        _build_course_list_item(course, db, current_user) for course in courses
    ]
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size
    }

@router.get("/{course_id}", response_model=schemas.CourseDetailOut)
async def get_course_detail(
    course_id: int,
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(auth.oauth2_scheme)
):
    """获取课程详情（无需登录）"""
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    current_user = await _optional_user(token, db)
    _require_course_access(course, current_user, db)
    
    # 检查是否已选课
    enrolled = False
    if current_user and current_user.role == "student":
        enrollment = db.query(models.Enrollment).filter(
            models.Enrollment.student_id == current_user.id,
            models.Enrollment.course_id == course_id,
            models.Enrollment.status == "active"
        ).first()
        enrolled = enrollment is not None
    
    # 统计选课人数
    enrollment_count = db.query(models.Enrollment).filter(
        models.Enrollment.course_id == course_id,
        models.Enrollment.status == "active"
    ).count()
    
    # 获取课程内容
    contents = db.query(models.CourseContent).filter(
        models.CourseContent.course_id == course_id
    ).order_by(models.CourseContent.order).all()
    
    # 构造返回数据
    return {
        "id": course.id,
        "title": course.title,
        "description": course.description,
        "cover_url": course.cover_url,
        "category": course.category,
        "is_public": course.is_public,
        "teacher_id": course.teacher_id,
        "created_at": course.created_at,
        "enrolled": enrolled,
        "enrollment_count": enrollment_count,
        "contents": contents
    }


# ==================== 课程内容管理 ====================

@router.post("/{course_id}/contents", response_model=schemas.CourseContentOut)
async def add_course_content(
    course_id: int,
    content_in: schemas.CourseContentCreate,
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    """新增课程章节/视频（仅教师）"""
    # 检查课程是否存在
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # 检查权限
    if course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to add content to this course")
    
    # 创建内容
    new_content = models.CourseContent(
        course_id=course_id,
        title=content_in.title,
        content_type=content_in.content_type,
        content_url=content_in.content_url,
        duration=content_in.duration,
        order=content_in.order
    )
    db.add(new_content)
    db.commit()
    db.refresh(new_content)
    return new_content


@router.get("/{course_id}/contents", response_model=List[schemas.CourseContentOut])
async def get_course_contents(
    course_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """列出课程章节"""
    # 检查课程是否存在
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    _require_course_access(course, current_user, db)
    contents = db.query(models.CourseContent).filter(
        models.CourseContent.course_id == course_id
    ).order_by(models.CourseContent.order).all()
    
    return contents

@router.put("/{course_id}/contents/{content_id}", response_model=schemas.CourseContentOut)
async def update_course_content(
    course_id: int,
    content_id: int,
    content_in: schemas.CourseContentCreate,
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    """更新课程章节（仅课程创建者）"""
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update content for this course")

    content = db.query(models.CourseContent).filter(
        models.CourseContent.id == content_id,
        models.CourseContent.course_id == course_id
    ).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    content.title = content_in.title
    content.content_type = content_in.content_type
    content.content_url = content_in.content_url
    content.duration = content_in.duration
    content.order = content_in.order
    db.commit()
    db.refresh(content)
    return content


@router.delete("/{course_id}/contents/{content_id}")
async def delete_course_content(
    course_id: int,
    content_id: int,
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db)
):
    """删除课程章节（仅课程创建者）"""
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete content from this course")

    content = db.query(models.CourseContent).filter(
        models.CourseContent.id == content_id,
        models.CourseContent.course_id == course_id
    ).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    db.query(models.CourseProgress).filter(
        models.CourseProgress.content_id == content_id
    ).delete(synchronize_session=False)
    db.delete(content)
    db.commit()
    return {"success": True}

@router.get("/content/{content_id}", response_model=schemas.CourseContentOut)
async def get_single_content(
    content_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """获取单个课程内容详情"""
    content = db.query(models.CourseContent).filter(
        models.CourseContent.id == content_id
    ).first()

    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    _require_course_access(content.course, current_user, db)
    return content


@router.get("/content/{content_id}/progress")
async def get_content_progress(
    content_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """获取单个内容的学习进度"""
    # 检查内容是否存在
    content = db.query(models.CourseContent).filter(
        models.CourseContent.id == content_id
    ).first()

    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    _require_student_enrollment(content.course, current_user, db)

    # 查找进度记录
    progress = db.query(models.CourseProgress).filter(
        models.CourseProgress.student_id == current_user.id,
        models.CourseProgress.content_id == content_id
    ).first()

    if not progress:
        # 返回默认进度
        return {
            "last_position": 0,
            "completed": False,
            "progress": 0.0
        }

    return {
        "last_position": progress.last_position,
        "completed": progress.completed,
        "progress": progress.progress
    }


@router.post("/content/{content_id}/progress")
async def save_content_progress(
    content_id: int,
    last_position: int,
    completed: bool = False,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """保存单个内容的学习进度"""
    # 检查内容是否存在
    content = db.query(models.CourseContent).filter(
        models.CourseContent.id == content_id
    ).first()

    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    _require_student_enrollment(content.course, current_user, db)

    # 查找或创建进度记录
    progress = db.query(models.CourseProgress).filter(
        models.CourseProgress.student_id == current_user.id,
        models.CourseProgress.content_id == content_id
    ).first()

    if not progress:
        progress = models.CourseProgress(
            student_id=current_user.id,
            content_id=content_id
        )
        db.add(progress)

    # 更新进度
    progress.last_position = last_position
    progress.completed = completed

    # 如果完成，设置进度为100
    if completed:
        progress.progress = 100.0
    elif content.duration and content.duration > 0:
        # 根据播放位置计算进度百分比
        progress.progress = min(100.0, (last_position / content.duration) * 100)

    db.commit()
    db.refresh(progress)

    return {
        "success": True,
        "last_position": progress.last_position,
        "completed": progress.completed,
        "progress": progress.progress
    }



# ==================== 选课管理 ====================

@router.get("/{course_id}/enrollments/manage")
async def list_course_enrollments(
    course_id: int,
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db),
):
    """课程教师查看当前有效学员名单。"""
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    _require_course_owner(course, current_user)

    rows = (
        db.query(models.Enrollment)
        .filter(
            models.Enrollment.course_id == course_id,
            models.Enrollment.status == "active",
        )
        .order_by(models.Enrollment.joined_at.desc())
        .all()
    )
    return [
        {
            "enrollment_id": row.id,
            "student_id": row.student_id,
            "student_no": row.student.student_id,
            "name": row.student.name,
            "class_name": row.student.plain_class_name,
            "joined_at": row.joined_at,
        }
        for row in rows
    ]


@router.post("/{course_id}/enrollments/{student_user_id}")
async def grant_course_enrollment(
    course_id: int,
    student_user_id: int,
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db),
):
    """课程教师向本人管辖学生授予课程学习权限。"""
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    _require_course_owner(course, current_user)

    managed = await get_managed_students_query(current_user, db)
    student = managed.filter(models.User.id == student_user_id).first()
    if not student:
        raise HTTPException(status_code=403, detail="该学生不在你的管辖范围内")

    enrollment = db.query(models.Enrollment).filter(
        models.Enrollment.course_id == course_id,
        models.Enrollment.student_id == student_user_id,
    ).first()
    if enrollment and enrollment.status == "active":
        return {"success": True, "already_enrolled": True}
    if enrollment:
        enrollment.status = "active"
        enrollment.joined_at = datetime.utcnow()
    else:
        enrollment = models.Enrollment(
            course_id=course_id,
            student_id=student_user_id,
            status="active",
        )
        db.add(enrollment)
    record_audit(
        db,
        actor=current_user,
        action="course.enrollment.grant",
        resource_type="course",
        resource_id=course_id,
        detail={"student_user_id": student_user_id},
    )
    db.commit()
    return {"success": True, "already_enrolled": False}


@router.delete("/{course_id}/enrollments/{student_user_id}")
async def revoke_course_enrollment(
    course_id: int,
    student_user_id: int,
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db),
):
    """课程教师撤销课程权限；学习历史继续保留。"""
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    _require_course_owner(course, current_user)
    enrollment = db.query(models.Enrollment).filter(
        models.Enrollment.course_id == course_id,
        models.Enrollment.student_id == student_user_id,
        models.Enrollment.status == "active",
    ).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="该学生当前没有课程权限")
    enrollment.status = "dropped"
    record_audit(
        db,
        actor=current_user,
        action="course.enrollment.revoke",
        resource_type="course",
        resource_id=course_id,
        detail={"student_user_id": student_user_id},
    )
    db.commit()
    return {"success": True}

@router.post("/{course_id}/enroll")
async def enroll_course(
    course_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """学生选课"""
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can enroll")
    
    # 检查课程是否存在
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if not course.is_public:
        raise HTTPException(status_code=403, detail="私有课程不能自行选课，请联系任课教师或管理员授权")
    
    # 检查是否已选课
    existing = db.query(models.Enrollment).filter(
        models.Enrollment.student_id == current_user.id,
        models.Enrollment.course_id == course_id
    ).first()
    
    if existing:
        if existing.status == "active":
            raise HTTPException(status_code=400, detail="Already enrolled")
        else:
            # 重新激活
            existing.status = "active"
            existing.joined_at = datetime.utcnow()
            db.commit()
            return {"success": True}
    
    # 创建选课记录
    enrollment = models.Enrollment(
        student_id=current_user.id,
        course_id=course_id
    )
    db.add(enrollment)
    db.commit()
    return {"success": True}


@router.delete("/{course_id}/enroll")
async def drop_course(
    course_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """退课"""
    enrollment = db.query(models.Enrollment).filter(
        models.Enrollment.student_id == current_user.id,
        models.Enrollment.course_id == course_id,
        models.Enrollment.status == "active"
    ).first()
    
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    
    enrollment.status = "dropped"
    db.commit()
    return {"success": True}


@router.get("/me/enrollments", response_model=List[schemas.EnrollmentOut])
async def get_my_enrollments(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """我已选课程列表"""
    enrollments = db.query(models.Enrollment).filter(
        models.Enrollment.student_id == current_user.id,
        models.Enrollment.status == "active"
    ).all()
    
    return enrollments


@router.get("/me/enrollments/{course_id}/progress")
async def get_course_progress(
    course_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """获取某课程的学习进度"""
    # 检查是否已选课
    enrollment = db.query(models.Enrollment).filter(
        models.Enrollment.student_id == current_user.id,
        models.Enrollment.course_id == course_id,
        models.Enrollment.status == "active"
    ).first()
    
    if not enrollment:
        raise HTTPException(status_code=404, detail="Not enrolled in this course")
    
    # 获取课程所有内容
    contents = db.query(models.CourseContent).filter(
        models.CourseContent.course_id == course_id
    ).all()
    
    if not contents:
        return {"percent": 0}
    
    # 获取学习进度
    content_ids = [c.id for c in contents]
    progress_records = db.query(models.CourseProgress).filter(
        models.CourseProgress.student_id == current_user.id,
        models.CourseProgress.content_id.in_(content_ids)
    ).all()
    
    # 计算总进度
    total_progress = sum(p.progress for p in progress_records)
    avg_progress = total_progress / len(contents) if contents else 0
    
    return {"percent": int(avg_progress)}


# ==================== 学习进度管理 ====================

@router.post("/progress", response_model=schemas.CourseProgressOut)
async def update_progress(
    progress_in: schemas.CourseProgressUpdate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """更新学习进度"""
    content = db.query(models.CourseContent).filter(
        models.CourseContent.id == progress_in.content_id
    ).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    _require_student_enrollment(content.course, current_user, db)
    # 查找或创建进度记录
    progress = db.query(models.CourseProgress).filter(
        models.CourseProgress.student_id == current_user.id,
        models.CourseProgress.content_id == progress_in.content_id
    ).first()
    
    if not progress:
        progress = models.CourseProgress(
            student_id=current_user.id,
            content_id=progress_in.content_id
        )
        db.add(progress)
    
    progress.progress = progress_in.progress
    if progress_in.last_position is not None:
        progress.last_position = progress_in.last_position
    
    if progress_in.progress >= 100:
        progress.completed = True
    
    db.commit()
    db.refresh(progress)
    return progress


# ==================== 兼容旧接口 ====================

@router.get("/my/enrollments", response_model=List[schemas.CourseOut])
async def get_my_courses(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """获取我的课程（已选课）- 兼容旧接口"""
    enrollments = db.query(models.Enrollment).filter(
        models.Enrollment.student_id == current_user.id,
        models.Enrollment.status == "active"
    ).all()
    
    course_ids = [e.course_id for e in enrollments]
    courses = db.query(models.Course).filter(models.Course.id.in_(course_ids)).all()
    
    return courses

