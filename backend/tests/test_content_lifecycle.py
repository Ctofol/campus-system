import asyncio
from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models
from app.database import Base
from app.routers import courses, teacher
from app.services.task_run_service import student_may_submit_task


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
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


def test_course_delete_archives_and_preserves_learning_history(db):
    owner = _user(db, "teacher", "教师")
    student = _user(db, "student", "学生")
    course = models.Course(title="课程", teacher_id=owner.id, is_public=True)
    db.add(course)
    db.flush()
    content = models.CourseContent(course_id=course.id, title="第一课", content_type="video")
    enrollment = models.Enrollment(student_id=student.id, course_id=course.id, status="active")
    db.add_all([content, enrollment])
    db.flush()
    progress = models.CourseProgress(student_id=student.id, content_id=content.id, progress=60)
    db.add(progress)
    db.commit()

    result = asyncio.run(courses.delete_course(course.id, owner, db))
    assert result == {"success": True, "archived": True}
    assert db.get(models.Course, course.id).lifecycle_status == "archived"
    assert db.query(models.CourseContent).filter_by(course_id=course.id).count() == 1
    assert db.query(models.Enrollment).filter_by(course_id=course.id).count() == 1
    assert db.query(models.CourseProgress).filter_by(content_id=content.id).count() == 1
    assert courses._may_view_course(course, student, db) is True
    assert courses._may_view_course(course, None, db) is False


def test_task_delete_archives_and_preserves_submissions(db):
    owner = _user(db, "teacher", "教师")
    student = _user(db, "student", "学生")
    task = models.Task(title="任务", type="run", created_by=owner.id)
    db.add(task)
    db.flush()
    activity = models.Activity(
        user_id=student.id,
        type="run",
        source="task",
        task_id=task.id,
        started_at=datetime.utcnow(),
        ended_at=datetime.utcnow(),
    )
    db.add(activity)
    db.commit()

    result = asyncio.run(teacher.delete_teacher_task(task.id, owner, db))
    assert result == {"success": True, "archived": True}
    assert db.get(models.Task, task.id).lifecycle_status == "archived"
    assert db.query(models.Activity).filter_by(task_id=task.id).count() == 1
    allowed, message = student_may_submit_task(student, task)
    assert allowed is False
    assert "关闭" in message
