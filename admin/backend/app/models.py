from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
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
    user = relationship("User", back_populates="profile", uselist=False)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, nullable=False)
    name = Column(String, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=True)
    student_id = Column(String, ForeignKey("student_profiles.student_id"), unique=True, nullable=True)
    gender = Column(String, nullable=True)
    major = Column(String, nullable=True)
    health_status = Column(String, default="normal")
    abnormal_reason = Column(String, nullable=True)
    group_name = Column(String, nullable=True)
    signature = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    regular_score = Column(Float, default=0.0)
    profile = relationship("StudentProfile", back_populates="user", foreign_keys=[student_id])
    student_class = relationship("Class", back_populates="students", foreign_keys=[class_id])
    health_requests = relationship("HealthRequest", back_populates="student")

class Class(Base):
    __tablename__ = "classes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    teacher = relationship("User", foreign_keys=[teacher_id])
    students = relationship("User", back_populates="student_class", foreign_keys="User.class_id")

class Activity(Base):
    __tablename__ = "activities"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String, nullable=False)
    source = Column(String, nullable=False)
    status = Column(String, default="finished")
    started_at = Column(DateTime, nullable=False)
    ended_at = Column(DateTime, nullable=False)
    is_valid = Column(Boolean, default=False)
    fail_reason = Column(String, nullable=True)
    face_verified = Column(Boolean, default=False)
    user = relationship("User")
    metrics = relationship("ActivityMetrics", back_populates="activity", uselist=False)


class TeacherClass(Base):
    __tablename__ = "teacher_classes"
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    class_name = Column(String, nullable=False)
    teacher = relationship("User", foreign_keys=[teacher_id])

class ActivityMetrics(Base):
    __tablename__ = "activity_metrics"
    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"))
    distance = Column(Float, nullable=True)
    duration = Column(Integer, nullable=False)
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
    scored_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    activity = relationship("Activity", back_populates="metrics")
    scorer = relationship("User", foreign_keys=[scored_by])

class HealthRequest(Base):
    __tablename__ = "health_requests"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String, nullable=False)
    reason = Column(String, nullable=True)
    attachments = Column(String, nullable=True)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    student = relationship("User", back_populates="health_requests")
