import asyncio

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models, schemas
from app.routers import courses


@pytest.fixture()
def db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    models.Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def _user(db, role, name):
    row = models.User(role=role, name=name, password_hash="test")
    db.add(row)
    db.flush()
    return row


def _course(db, teacher, *, public):
    row = models.Course(title="权限课程", teacher_id=teacher.id, is_public=public)
    db.add(row)
    db.flush()
    content = models.CourseContent(course_id=row.id, title="第一课", content_type="video", content_url="/private.mp4")
    db.add(content)
    db.commit()
    return row, content


def test_anonymous_user_only_sees_public_courses(db):
    teacher = _user(db, "teacher", "教师")
    public, _ = _course(db, teacher, public=True)
    private, _ = _course(db, teacher, public=False)
    result = asyncio.run(courses.get_courses(db=db, token=None))
    assert [item["id"] for item in result["items"]] == [public.id]
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(courses.get_course_detail(private.id, db, None))
    assert exc_info.value.status_code == 403


def test_enrolled_student_can_read_private_course_but_other_student_cannot(db):
    teacher = _user(db, "teacher", "教师")
    enrolled = _user(db, "student", "已授权学生")
    outside = _user(db, "student", "未授权学生")
    private, content = _course(db, teacher, public=False)
    db.add(models.Enrollment(student_id=enrolled.id, course_id=private.id, status="active"))
    db.commit()

    assert courses._may_view_course(private, enrolled, db) is True
    assert courses._may_view_course(private, outside, db) is False
    assert asyncio.run(courses.get_course_contents(private.id, enrolled, db))[0].id == content.id
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(courses.get_course_contents(private.id, outside, db))
    assert exc_info.value.status_code == 403
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(courses.get_single_content(content.id, outside, db))
    assert exc_info.value.status_code == 403


def test_private_course_cannot_be_self_enrolled_and_progress_requires_enrollment(db):
    teacher = _user(db, "teacher", "教师")
    student = _user(db, "student", "学生")
    private, private_content = _course(db, teacher, public=False)
    public, public_content = _course(db, teacher, public=True)

    with pytest.raises(HTTPException, match="不能自行选课"):
        asyncio.run(courses.enroll_course(private.id, student, db))
    with pytest.raises(HTTPException, match="请先选课"):
        asyncio.run(courses.save_content_progress(public_content.id, 10, False, student, db))

    asyncio.run(courses.enroll_course(public.id, student, db))
    result = asyncio.run(courses.save_content_progress(public_content.id, 10, False, student, db))
    assert result["success"] is True
    with pytest.raises(HTTPException, match="请先选课"):
        asyncio.run(courses.update_progress(schemas.CourseProgressUpdate(content_id=private_content.id, progress=50), student, db))


def test_owner_teacher_and_admin_can_view_private_course(db):
    owner = _user(db, "teacher", "任课教师")
    other_teacher = _user(db, "teacher", "其他教师")
    admin = _user(db, "admin", "管理员")
    private, _ = _course(db, owner, public=False)
    assert courses._may_view_course(private, owner, db) is True
    assert courses._may_view_course(private, admin, db) is True
    assert courses._may_view_course(private, other_teacher, db) is False


def test_teacher_can_only_grant_managed_student_course_access(db, monkeypatch):
    owner = _user(db, "teacher", "任课教师")
    managed_student = _user(db, "student", "管辖学生")
    outside_student = _user(db, "student", "其他学生")
    private, _ = _course(db, owner, public=False)

    async def managed_query(_teacher, session):
        return session.query(models.User).filter(models.User.id == managed_student.id)

    monkeypatch.setattr(courses, "get_managed_students_query", managed_query)
    result = asyncio.run(courses.grant_course_enrollment(private.id, managed_student.id, owner, db))
    assert result == {"success": True, "already_enrolled": False}
    assert courses._may_view_course(private, managed_student, db) is True

    with pytest.raises(HTTPException, match="不在你的管辖范围"):
        asyncio.run(courses.grant_course_enrollment(private.id, outside_student.id, owner, db))
    assert courses._may_view_course(private, outside_student, db) is False

    rows = asyncio.run(courses.list_course_enrollments(private.id, owner, db))
    assert [row["student_id"] for row in rows] == [managed_student.id]
    asyncio.run(courses.revoke_course_enrollment(private.id, managed_student.id, owner, db))
    assert courses._may_view_course(private, managed_student, db) is False
