from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, nullable=False)  # 'student' | 'teacher'
    name = Column(String, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=True)
    student_id = Column(String, unique=True, nullable=True) # 学号
    health_status = Column(String, default="normal") # normal, leave, injured
    abnormal_reason = Column(String, nullable=True)
    group_name = Column(String, nullable=True)

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
    type = Column(String, nullable=False)  # 'run' | 'test'
    source = Column(String, nullable=False)  # 'free' | 'task'
    status = Column(String, default="finished")  # 'finished' | 'approved'
    started_at = Column(DateTime, nullable=False)
    ended_at = Column(DateTime, nullable=False)

    user = relationship("User")
    metrics = relationship("ActivityMetrics", back_populates="activity", uselist=False)
    evidence = relationship("ActivityEvidence", back_populates="activity")
    review = relationship("ActivityReview", back_populates="activity", uselist=False)

    @property
    def student_name(self):
        return self.user.name if self.user else "Unknown"

class ActivityMetrics(Base):
    __tablename__ = "activity_metrics"

    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"))
    distance = Column(Float, nullable=True)  # 跑步距离（km）
    duration = Column(Integer, nullable=False)  # 时长（秒）
    pace = Column(String, nullable=True)  # 配速
    trajectory = Column(String, nullable=True)  # 运动轨迹 (JSON String)
    checkpoints = Column(String, nullable=True)  # 打卡记录 (JSON String)
    count = Column(Integer, nullable=True)  # 体测次数
    qualified = Column(Boolean, default=False)  # 是否达标

    activity = relationship("Activity", back_populates="metrics")

class Checkpoint(Base):
    __tablename__ = "checkpoints"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    radius = Column(Integer, default=50) # meters
    description = Column(String, nullable=True)

class ActivityEvidence(Base):
    __tablename__ = "activity_evidence"

    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"))
    evidence_type = Column(String, nullable=False)  # 'gps' | 'camera'
    data_ref = Column(String, nullable=False)  # JSON 或 文件路径

    activity = relationship("Activity", back_populates="evidence")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    type = Column(String, nullable=False)  # 'run' | 'test'
    min_distance = Column(Float, nullable=True)
    min_duration = Column(Integer, nullable=True)
    min_count = Column(Integer, nullable=True)
    deadline = Column(DateTime, nullable=True)
    description = Column(String, nullable=True)
    target_group = Column(String, default="all") # 'all', 'group_a', etc.
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"))  # teacher_id
    created_at = Column(DateTime, default=datetime.utcnow)

    creator = relationship("User")
    target_class = relationship("Class")

class ActivityReview(Base):
    __tablename__ = "activity_review"

    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"))
    teacher_id = Column(Integer, ForeignKey("users.id"))
    result = Column(String, default="approved")  # 'approved'
    reviewed_at = Column(DateTime, default=datetime.utcnow)

    teacher = relationship("User")
    activity = relationship("Activity", back_populates="review")

class HealthRequest(Base):
    __tablename__ = "health_requests"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String, nullable=False)  # 'leave' | 'injury'
    reason = Column(String, nullable=True)
    status = Column(String, default="pending")  # 'pending' | 'approved' | 'rejected'
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student = relationship("User", back_populates="health_requests")
