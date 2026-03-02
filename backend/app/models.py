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
    video_url = Column(String, nullable=True)  # 视频文件URL
    score = Column(Integer, nullable=True)  # AI评分（0-100）
    score_detail = Column(String, nullable=True)  # 评分详情（JSON字符串）

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

# Course Models (Phase 4.2)
class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    cover_url = Column(String, nullable=True)  # 修改为 cover_url 以匹配数据库
    teacher_id = Column(Integer, ForeignKey("users.id"))
    category = Column(String, nullable=True)  # 'theory' | 'skill' | 'fitness'
    is_public = Column(Boolean, default=True)  # 是否全校公开
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    teacher = relationship("User", foreign_keys=[teacher_id])
    contents = relationship("CourseContent", back_populates="course")
    enrollments = relationship("Enrollment", back_populates="course")

class CourseContent(Base):
    __tablename__ = "course_contents"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    title = Column(String, nullable=False)
    content_type = Column(String, nullable=False)  # 'video' | 'document' | 'link'
    content_url = Column(String, nullable=True)  # 外部链接或本地路径
    duration = Column(Integer, nullable=True)  # 视频时长（秒）
    order = Column(Integer, default=0)  # 排序
    created_at = Column(DateTime, default=datetime.utcnow)

    course = relationship("Course", back_populates="contents")
    progress_records = relationship("CourseProgress", back_populates="content")

class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    joined_at = Column(DateTime, default=datetime.utcnow)  # 修改为 joined_at 以匹配数据库
    status = Column(String, default="active")  # 'active' | 'completed' | 'dropped'

    student = relationship("User", foreign_keys=[student_id])
    course = relationship("Course", back_populates="enrollments")

class CourseProgress(Base):
    __tablename__ = "course_progress"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    content_id = Column(Integer, ForeignKey("course_contents.id"))
    progress = Column(Float, default=0.0)  # 0-100
    completed = Column(Boolean, default=False)
    last_position = Column(Integer, default=0)  # 视频播放位置（秒）
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student = relationship("User", foreign_keys=[student_id])
    content = relationship("CourseContent", back_populates="progress_records")


# Run Group Models (跑团联盟)
class RunGroup(Base):
    __tablename__ = "run_groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    avatar = Column(String, nullable=True)
    creator_id = Column(Integer, ForeignKey("users.id"))
    total_mileage = Column(Float, default=0.0)  # 总里程
    member_count = Column(Integer, default=1)  # 成员数
    rank = Column(Integer, nullable=True)  # 排名
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    creator = relationship("User", foreign_keys=[creator_id])
    members = relationship("RunGroupMember", back_populates="group")
    activities = relationship("RunGroupActivity", back_populates="group")


class RunGroupMember(Base):
    __tablename__ = "run_group_members"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("run_groups.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String, default="member")  # 'creator' | 'admin' | 'member'
    total_mileage = Column(Float, default=0.0)  # 个人在跑团的总里程
    joined_at = Column(DateTime, default=datetime.utcnow)

    group = relationship("RunGroup", back_populates="members")
    user = relationship("User")


class RunGroupActivity(Base):
    __tablename__ = "run_group_activities"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("run_groups.id"))
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    activity_time = Column(DateTime, nullable=False)
    location = Column(String, nullable=True)
    distance = Column(Float, nullable=True)  # 目标距离
    total_quota = Column(Integer, default=100)  # 总名额
    apply_count = Column(Integer, default=0)  # 已报名人数
    status = Column(String, default="upcoming")  # 'upcoming' | 'ongoing' | 'finished'
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    group = relationship("RunGroup", back_populates="activities")
    creator = relationship("User", foreign_keys=[created_by])
    applications = relationship("RunGroupActivityApplication", back_populates="activity")


class RunGroupActivityApplication(Base):
    __tablename__ = "run_group_activity_applications"

    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("run_group_activities.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String, default="applied")  # 'applied' | 'participated' | 'cancelled'
    applied_at = Column(DateTime, default=datetime.utcnow)

    activity = relationship("RunGroupActivity", back_populates="applications")
    user = relationship("User")
