"""
Course Management Router (Phase 4.2 Enhanced)
课程管理路由 - 完整的CRUD + 选课 + 进度管理
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/courses", tags=["courses"])


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
    """删除课程（仅教师）"""
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # 检查权限
    if course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this course")
    
    # 删除相关数据
    db.query(models.CourseProgress).filter(
        models.CourseProgress.content_id.in_(
            db.query(models.CourseContent.id).filter(models.CourseContent.course_id == course_id)
        )
    ).delete(synchronize_session=False)
    
    db.query(models.CourseContent).filter(models.CourseContent.course_id == course_id).delete()
    db.query(models.Enrollment).filter(models.Enrollment.course_id == course_id).delete()
    db.delete(course)
    db.commit()
    
    return {"success": True}


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
    # 尝试获取当前用户（如果有token）
    current_user = None
    if token:
        try:
            current_user = await auth.get_current_user(token, db)
        except:
            pass  # 忽略认证错误，允许未登录访问
    
    query = db.query(models.Course)
    
    # 学生只能看公开课程或已选课程
    if current_user and current_user.role == "student":
        query = query.filter(models.Course.is_public == True)
    
    # 按分类筛选
    if category:
        query = query.filter(models.Course.category == category)
    
    # 按教师筛选
    if teacher_id:
        query = query.filter(models.Course.teacher_id == teacher_id)
    
    total = query.count()
    courses = query.order_by(models.Course.created_at.desc()).offset((page - 1) * size).limit(size).all()
    
    # 为每个课程添加 enrolled 和 enrollment_count 字段
    items = []
    for course in courses:
        # 检查是否已选课
        enrolled = False
        if current_user and current_user.role == "student":
            enrollment = db.query(models.Enrollment).filter(
                models.Enrollment.student_id == current_user.id,
                models.Enrollment.course_id == course.id,
                models.Enrollment.status == "active"
            ).first()
            enrolled = enrollment is not None
        
        # 统计选课人数
        enrollment_count = db.query(models.Enrollment).filter(
            models.Enrollment.course_id == course.id,
            models.Enrollment.status == "active"
        ).count()
        
        # 构造课程数据
        course_dict = {
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "cover_url": course.cover_url,
            "category": course.category,
            "is_public": course.is_public,
            "teacher_id": course.teacher_id,
            "created_at": course.created_at,
            "enrolled": enrolled,
            "enrollment_count": enrollment_count
        }
        items.append(course_dict)
    
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
    
    # 尝试获取当前用户（如果有token）
    current_user = None
    if token:
        try:
            current_user = await auth.get_current_user(token, db)
        except:
            pass  # 忽略认证错误，允许未登录访问
    
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
    
    # 获取内容列表，按order排序
    contents = db.query(models.CourseContent).filter(
        models.CourseContent.course_id == course_id
    ).order_by(models.CourseContent.order).all()
    
    return contents

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



# ==================== 单个内容查询和进度管理 ====================

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

