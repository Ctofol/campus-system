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
    count = Column(Integer, nullable=True)  # 体测次数
    qualified = Column(Boolean, default=False)  # 是否达标

    activity = relationship("Activity", back_populates="metrics")

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
    created_by = Column(Integer, ForeignKey("users.id"))  # teacher_id
    created_at = Column(DateTime, default=datetime.utcnow)

    creator = relationship("User")

class ActivityReview(Base):
    __tablename__ = "activity_review"

    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"))
    teacher_id = Column(Integer, ForeignKey("users.id"))
    result = Column(String, default="approved")  # 'approved'
    reviewed_at = Column(DateTime, default=datetime.utcnow)

    activity = relationship("Activity", back_populates="review")
    teacher = relationship("User")
