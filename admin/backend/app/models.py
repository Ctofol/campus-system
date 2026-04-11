from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from datetime import datetime
from .database import Base


class StudentProfile(Base):
    __tablename__ = "student_profiles"
    student_id = Column(String, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    class_name = Column(String, nullable=False)
    major = Column(String, nullable=True)
    is_activated = Column(Boolean, default=False)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, nullable=False)
    name = Column(String, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    class_id = Column(Integer, nullable=True)
    major_id = Column(Integer, nullable=True)
    student_id = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    major_name = Column(String, nullable=True)
    subject = Column(String, nullable=True)
    health_status = Column(String, default="normal")
    abnormal_reason = Column(String, nullable=True)
    group_name = Column(String, nullable=True)
    signature = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    regular_score = Column(Float, default=0.0)


class Class(Base):
    __tablename__ = "classes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    teacher_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Activity(Base):
    __tablename__ = "activities"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    type = Column(String, nullable=False)
    source = Column(String, nullable=False)
    status = Column(String, default="finished")
    started_at = Column(DateTime, nullable=False)
    ended_at = Column(DateTime, nullable=False)
    is_valid = Column(Boolean, default=False)
    fail_reason = Column(String, nullable=True)
    face_verified = Column(Boolean, default=False)


class TeacherClass(Base):
    __tablename__ = "teacher_classes"
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, nullable=False)
    class_name = Column(String, nullable=False)


class ActivityMetrics(Base):
    __tablename__ = "activity_metrics"
    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, nullable=True)
    distance = Column(Float, nullable=True)
    duration = Column(Integer, nullable=True)
    pace = Column(String, nullable=True)
    trajectory = Column(String, nullable=True)
    checkpoints = Column(String, nullable=True)
    count = Column(Integer, nullable=True)
    qualified = Column(Boolean, default=False)
    video_url = Column(String, nullable=True)
    score = Column(Integer, nullable=True)
    score_detail = Column(String, nullable=True)
    teacher_score = Column(Float, nullable=True)
    teacher_comment = Column(String, nullable=True)
    scored_at = Column(DateTime, nullable=True)
    scored_by = Column(Integer, nullable=True)


class HealthRequest(Base):
    __tablename__ = "health_requests"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, nullable=True)
    type = Column(String, nullable=False)
    reason = Column(String, nullable=True)
    attachments = Column(String, nullable=True)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)