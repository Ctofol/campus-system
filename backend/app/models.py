from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class StudentProfile(Base):
    """
    学生档案表：
    - 由管理员/导入接口预先创建
    - 注册时通过学号 + 姓名进行激活
    """
    __tablename__ = "student_profiles"

    student_id = Column(String, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    gender = Column(String, nullable=False)  # 'male' | 'female'
    class_name = Column(String, nullable=False)
    # 专业/课程（例如：刑侦技术、治安管理等）
    major = Column(String, nullable=True)
    # 选科（例如：篮球、羽毛球）
    subject = Column(String, nullable=True)
    is_activated = Column(Boolean, default=False)

    user = relationship("User", back_populates="profile", uselist=False)


# 新增：专业模型
class Major(Base):
    __tablename__ = "majors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)   # 如 “信息安全”

    classes = relationship("Class", back_populates="major")
    students = relationship("User", back_populates="major_rel")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, nullable=False)  # 'student' | 'teacher'
    name = Column(String, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 学生属性
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=True)
    major_id = Column(Integer, ForeignKey("majors.id"), nullable=True)
    student_id = Column(String, ForeignKey("student_profiles.student_id"), unique=True, nullable=True)
    gender = Column(String, nullable=True)
    major_name = Column(String, nullable=True) # 冗余字段或来自档案
    subject = Column(String, nullable=True) # 选科
    
    health_status = Column(String, default="normal")
    abnormal_reason = Column(String, nullable=True)
    group_name = Column(String, nullable=True)
    signature = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    header_bg_url = Column(String, nullable=True)
    regular_score = Column(Float, default=0.0)
    weekly_run_goal_km = Column(Float, nullable=True)  # 学生首页本周跑步目标（公里）

    profile = relationship("StudentProfile", back_populates="user", foreign_keys=[student_id])
    student_class = relationship("Class", back_populates="students", foreign_keys=[class_id])
    major_rel = relationship("Major", back_populates="students", foreign_keys=[major_id])
    health_requests = relationship("HealthRequest", back_populates="student")
    # 教师选科
    teacher_subjects = relationship("TeacherSubject", back_populates="teacher")

    @property
    def major(self):
        if self.major_rel:
            return self.major_rel.name
        if self.major_name:
            return self.major_name
        # 有行政班但缺少 major_id / major_name 的旧数据：从班级绑定的专业推断
        cls = self.student_class
        if cls and cls.major:
            return cls.major.name
        return None

    @property
    def plain_class_name(self):
        """行政班级名称（classes.name），不含专业前缀；专业见 major。"""
        return self.student_class.name if self.student_class else None

    @property
    def class_name(self):
        """展示用：专业名 + 班级名（与 plain_class_name、major 并用时会显得重复，教师端/历史接口仍依赖此格式）。"""
        if self.student_class:
            m_name = self.student_class.major.name if self.student_class.major else ""
            return f"{m_name} {self.student_class.name}".strip()
        return None


class Class(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False) # 如 "1区"
    major_id = Column(Integer, ForeignKey("majors.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    major = relationship("Major", back_populates="classes")
    teacher = relationship("User", foreign_keys=[teacher_id])
    students = relationship("User", back_populates="student_class", foreign_keys="User.class_id")

    @property
    def major_name(self):
        return self.major.name if self.major else None


class SunshineRunRule(Base):
    """班级常态化阳光跑规则。"""

    __tablename__ = "sunshine_run_rules"
    __table_args__ = (
        UniqueConstraint("class_id", name="uq_sunshine_rule_class"),
    )

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False, index=True)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    weekly_required_count = Column(Integer, default=3, nullable=False)
    min_distance_km = Column(Float, default=2.0, nullable=False)
    min_duration_sec = Column(Integer, default=0, nullable=False)
    min_pace = Column(Float, default=3.0, nullable=False)
    max_pace = Column(Float, default=10.0, nullable=False)
    enabled = Column(Boolean, default=True, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    target_class = relationship("Class")
    teacher = relationship("User", foreign_keys=[teacher_id])


# 新增：教师选科模型
class TeacherSubject(Base):
    __tablename__ = "teacher_subjects"

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject_name = Column(String, nullable=False) # 如 "篮球"

    teacher = relationship("User", back_populates="teacher_subjects")


class SubjectOption(Base):
    """全校可选体育专项（管理端维护）；教师管辖选科、档案/注册选科建议与此一致。"""

    __tablename__ = "subject_options"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    sort_order = Column(Integer, default=0, nullable=False)
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
    is_valid = Column(Boolean, default=False)  # 自由跑：阳光跑达标；任务跑：是否满足任务要求
    fail_reason = Column(String, nullable=True)  # 不达标原因
    face_verified = Column(Boolean, default=False)  # 人脸验证结果
    face_liveness_pass = Column(Boolean, nullable=True)  # 起止活体是否通过
    face_match_score = Column(Float, nullable=True)  # 起止 1:1 相似度 0-100
    face_fail_code = Column(String(64), nullable=True)  # LIVENESS_FAIL / NOT_SAME_PERSON / MISSING_PHOTO
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)  # 任务跑步关联

    user = relationship("User")
    task = relationship("Task", back_populates="activities", foreign_keys=[task_id])
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
    pace = Column(String, nullable=True)  # 配速（分/公里）
    trajectory = Column(String, nullable=True)  # 运动轨迹 (JSON String)
    checkpoints = Column(String, nullable=True)  # 打卡记录 (JSON String)
    count = Column(Integer, nullable=True)  # 体测次数
    step_count = Column(Integer, nullable=True)  # 步数
    qualified = Column(Boolean, default=False)  # 是否达标
    video_url = Column(String, nullable=True, default=None)  # 视频文件URL
    score = Column(Integer, nullable=True)  # AI评分（0-100）
    score_detail = Column(String, nullable=True)  # 评分详情（JSON字符串）
    teacher_score = Column(Float, nullable=True)  # 教师打分（第三阶段新增）
    teacher_comment = Column(String, nullable=True)  # 教师评语（第三阶段新增）
    scored_at = Column(DateTime, nullable=True)  # 打分时间（第三阶段新增）
    scored_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # 打分教师ID（第三阶段新增）
    exercise_type = Column(String(32), nullable=True)  # pull_up | sit_up | push_up
    analysis_status = Column(String(32), nullable=True)  # pending | success | failed
    analysis_error = Column(String(512), nullable=True)

    activity = relationship("Activity", back_populates="metrics")
    scorer = relationship("User", foreign_keys=[scored_by])  # 打分教师

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
    starts_at = Column(DateTime, nullable=True)  # 任务生效开始时间，空表示发布后即可参与
    description = Column(String, nullable=True)
    target_group = Column(String, default="all") # 'all', 'group_a', etc.
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"))  # teacher_id
    created_at = Column(DateTime, default=datetime.utcnow)
    video_url = Column(String, nullable=True)  # 体测任务视频URL（第二阶段新增）

    creator = relationship("User")
    target_class = relationship("Class")
    activities = relationship("Activity", back_populates="task", foreign_keys="Activity.task_id")

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
    attachments = Column(String, nullable=True)  # JSON array of file URLs
    status = Column(String, default="pending")  # 'pending' | 'approved' | 'rejected'
    # 请假时间（仅当 type == 'leave' 时有值）
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student = relationship("User", back_populates="health_requests")


class UserNotification(Base):
    """学生/教师站内通知（审批结果、任务提醒等）"""
    __tablename__ = "user_notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    title = Column(String, nullable=False)
    body = Column(String, nullable=True)
    ntype = Column(String, default="system", index=True)  # health_review | task | system
    payload = Column(String, nullable=True)
    is_read = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", backref="notifications")


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
    total_mileage = Column(Float, default=0.0, nullable=False)  # 总里程
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
    cover_image = Column(String, nullable=True)  # 活动封面图片
    activity_time = Column(DateTime, nullable=False)
    location = Column(String, nullable=True)
    distance = Column(Float, nullable=True)  # 目标距离
    total_quota = Column(Integer, default=100)  # 总名额
    apply_count = Column(Integer, default=0)  # 已报名人数
    status = Column(String, default="upcoming")  # 'upcoming' | 'ongoing' | 'finished'
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    group = relationship("RunGroup", back_populates="activities")
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


class TeacherClass(Base):
    """
    教师与班级的绑定关系：
    - 支持一个教师管理多个班级（通过班级名称）
    - 教师端所有学生/跑步/异常统计接口都应基于该表进行数据过滤
    """
    __tablename__ = "teacher_classes"

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    class_name = Column(String, nullable=False)

    teacher = relationship("User", foreign_keys=[teacher_id])


class TeacherStudent(Base):
    """
    管理员为教师显式绑定的学员（学生用户 id）。
    与管辖选科、行政班、Class.teacher_id 并存，合并进教师端管辖学生查询。
    """

    __tablename__ = "teacher_students"
    __table_args__ = (
        UniqueConstraint("teacher_id", "student_user_id", name="uq_teacher_student_user"),
    )

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    student_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    teacher = relationship("User", foreign_keys=[teacher_id])
    student = relationship("User", foreign_keys=[student_user_id])


class Medal(Base):
    __tablename__ = "medals"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(32), unique=True, nullable=False)  # e.g. 'run_5k', 'streak_100'
    name = Column(String(64), nullable=False)
    description = Column(String(256), nullable=False)
    icon_path = Column(String(256), nullable=False)  # e.g. '/static/medals/medal-distance-5k.png'


class UserMedal(Base):
    __tablename__ = "user_medals"
    __table_args__ = (
        UniqueConstraint("user_id", "medal_id", name="uq_user_medal"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    medal_id = Column(Integer, ForeignKey("medals.id"), nullable=False)
    earned_at = Column(DateTime, default=datetime.utcnow)

    medal = relationship("Medal")
