from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Auth
class UserBase(BaseModel):
    phone: str
    name: str
    role: str = "student"

class UserCreate(UserBase):
    password: str
    captcha_code: str
    captcha_key: str
    # 学生注册专用：用于与 StudentProfile 进行档案匹配
    student_id: str | None = None

class UserLogin(BaseModel):
    phone: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    user_id: int
    name: str
    class_name: Optional[str] = None
    student_id: Optional[str] = None
    major: Optional[str] = None

class UserProfile(BaseModel):
    id: int
    name: str
    phone: str
    role: str
    class_name: Optional[str] = None
    student_id: Optional[str] = None
    major: Optional[str] = None
    group_name: Optional[str] = None
    health_status: str
    signature: Optional[str] = None
    avatar_url: Optional[str] = None
    
    class Config:
        from_attributes = True

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    signature: Optional[str] = None
    avatar_url: Optional[str] = None

class TokenData(BaseModel):
    phone: str | None = None
    role: str | None = None

#
# Student Profile (档案激活用)
#

class StudentProfileBase(BaseModel):
    student_id: str
    full_name: str
    gender: str  # 'male' | 'female'
    class_name: str
    major: Optional[str] = None


class StudentProfileCreate(StudentProfileBase):
    pass


class StudentProfileOut(StudentProfileBase):
    is_activated: bool

    class Config:
        from_attributes = True

# Class
class ClassBase(BaseModel):
    name: str

class ClassCreate(ClassBase):
    pass

class ClassBind(BaseModel):
    class_ids: List[int]

class ClassOut(ClassBase):
    id: int
    teacher_id: Optional[int] = None
    student_count: int = 0
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class StudentInfo(UserBase):
    id: int
    class_id: Optional[int] = None
    
    class Config:
        from_attributes = True

class ClassDetail(ClassOut):
    students: List[StudentInfo] = []

# Metrics & Evidence
class ActivityMetricsCreate(BaseModel):
    distance: Optional[float] = None
    duration: int
    pace: Optional[str] = None
    trajectory: Optional[str] = None # JSON string of coordinates
    checkpoints: Optional[str] = None # JSON string of check-in data
    count: Optional[int] = None
    qualified: bool = False
    step_count: Optional[int] = None  # 步数
    video_url: Optional[str] = None  # 视频文件URL
    score: Optional[int] = None  # AI评分（0-100）
    score_detail: Optional[str] = None  # 评分详情（JSON字符串）

class ActivityEvidenceCreate(BaseModel):
    evidence_type: str
    data_ref: str

class ActivityMetricsOut(ActivityMetricsCreate):
    id: int
    activity_id: int
    class Config:
        from_attributes = True

class ActivityEvidenceOut(ActivityEvidenceCreate):
    id: int
    activity_id: int
    class Config:
        from_attributes = True

# Activity
class ActivityFinish(BaseModel):
    type: str  # 'run' | 'test'
    source: str = "free" # 'free' | 'task'
    started_at: datetime
    ended_at: datetime
    metrics: ActivityMetricsCreate
    evidence: List[ActivityEvidenceCreate] = []

class ActivityReviewOut(BaseModel):
    id: int
    teacher_id: int
    result: str
    reviewed_at: datetime
    class Config:
        from_attributes = True

class ActivityOut(BaseModel):
    id: int
    user_id: int
    type: str
    source: str
    status: str
    started_at: datetime
    ended_at: datetime
    metrics: Optional[ActivityMetricsOut] = None
    evidence: List[ActivityEvidenceOut] = []
    review: Optional[ActivityReviewOut] = None
    # 阳光跑相关的实时判定结果
    is_valid: Optional[bool] = None
    fail_reason: Optional[str] = None
    face_verified: Optional[bool] = None
    today_completed: Optional[bool] = None

    class Config:
        from_attributes = True

# Teacher
class ApproveRequest(BaseModel):
    result: str = "approved"


class InvalidActivityOut(BaseModel):
    id: int
    student_name: str
    student_id: Optional[str] = None
    class_name: Optional[str] = None
    fail_reason: Optional[str] = None
    distance: Optional[float] = None
    duration: Optional[int] = None
    pace: Optional[str] = None
    started_at: datetime
    start_photo_url: Optional[str] = None
    end_photo_url: Optional[str] = None


class ResolveActivityExceptionRequest(BaseModel):
    action: str  # 'confirm_cheat' | 'restore_valid'


class TeacherActivityListOut(ActivityOut):
    student_name: str

    class Config:
        from_attributes = True

class ActivityListResponse(BaseModel):
    items: List[ActivityOut]
    total: int
    page: int
    size: int

class TeacherActivityListResponse(BaseModel):
    items: List[TeacherActivityListOut]
    total: int
    page: int
    size: int

# Task
class TaskCreate(BaseModel):
    title: str
    type: str
    min_distance: Optional[float] = 0.0
    min_duration: Optional[int] = 0
    min_count: Optional[int] = 0
    deadline: Optional[datetime] = None
    description: Optional[str] = None
    target_group: Optional[str] = "all"
    class_id: Optional[int] = None
    video_url: Optional[str] = None  # 体测任务视频URL（第二阶段新增）

class TaskOut(TaskCreate):
    id: int
    created_by: int
    
    class Config:
        from_attributes = True

class TaskListStats(TaskOut):
    total_students: int
    completed_count: int

class TaskListResponse(BaseModel):
    items: List[TaskListStats]
    total: int
    page: int
    size: int

class StudentTaskOut(TaskOut):
    status: str # 'pending', 'completed', 'expired'
    progress: float # percentage or value

class StudentTaskListResponse(BaseModel):
    items: List[StudentTaskOut]
    total: int
    page: int
    size: int

class StudentCompletionStatus(BaseModel):
    student_id: int
    student_name: str
    status: str # 'completed', 'pending'
    completed_at: Optional[datetime] = None
    metric_value: Optional[str] = None # e.g. "2.5km" or "15 mins"
    activity_id: Optional[int] = None  # 第三阶段新增：活动ID，用于打分
    teacher_score: Optional[float] = None  # 第三阶段新增：教师打分

# 第三阶段新增：教师打分相关schemas
class TeacherScoreCreate(BaseModel):
    activity_id: int
    score: float  # 0-100
    comment: Optional[str] = None

class TeacherScoreUpdate(BaseModel):
    score: float  # 0-100
    comment: Optional[str] = None

class TeacherScoreOut(BaseModel):
    id: int
    activity_id: int
    student_id: int
    student_name: str
    teacher_score: Optional[float] = None
    teacher_comment: Optional[str] = None
    scored_at: Optional[datetime] = None
    scored_by: Optional[int] = None
    
    class Config:
        from_attributes = True

class StudentScoreRecord(BaseModel):
    task_id: int
    task_title: str
    activity_id: int
    score: Optional[float] = None
    comment: Optional[str] = None
    scored_at: Optional[datetime] = None
    
class StudentScoreHistory(BaseModel):
    student_id: int
    student_name: str
    regular_score: float  # 平时分
    score_records: List[StudentScoreRecord]

class TaskDetailStats(TaskOut):
    total_students: int
    completed_count: int
    student_statuses: List[StudentCompletionStatus] = []

# Checkpoint
class CheckpointBase(BaseModel):
    name: str
    latitude: float
    longitude: float
    radius: int = 50
    description: Optional[str] = None

class CheckpointCreate(CheckpointBase):
    pass

class CheckpointOut(CheckpointBase):
    id: int
    class Config:
        from_attributes = True

# Health & Student Management
class HealthRequestCreate(BaseModel):
    type: str  # 'leave' | 'injury'
    reason: str
    # 请假开始/结束时间（仅 type == 'leave' 时必填）
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    attachments: Optional[List[str]] = []  # List of file URLs

class HealthRequestOut(HealthRequestCreate):
    id: int
    student_id: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class StudentDetail(StudentInfo):
    student_id: Optional[str] = None
    health_status: str = "normal"
    abnormal_reason: Optional[str] = None
    group_name: Optional[str] = None
    health_requests: List[HealthRequestOut] = []

class StudentUpdate(BaseModel):
    student_id: Optional[str] = None
    health_status: Optional[str] = None
    abnormal_reason: Optional[str] = None
    group_name: Optional[str] = None
    class_id: Optional[int] = None

class BulkUpdateStudent(BaseModel):
    student_ids: List[int]
    health_status: Optional[str] = None
    abnormal_reason: Optional[str] = None
    group_name: Optional[str] = None
    class_id: Optional[int] = None

class CheckInRequest(BaseModel):
    lat: float
    lng: float
    checkpoint_id: int

class TeacherStatsOut(BaseModel):
    student_count: int
    today_checkin: int
    abnormal_count: int
    pending_approvals: int
    pending_health: int = 0  # 请假待处理数量（HealthRequest status=pending）
    pending_activities: int = 0  # 运动待审批数量（Activity status=pending_review）
    avg_pace: str
    task_count: int
    compliance_rate: int
    qualified_rate: int  # 达标率（百分整数）
    completion_rate: int  # 完成率（百分整数）

class TodoItem(BaseModel):
    id: str
    title: str
    type: str  # 'approval' | 'task'
    desc: str
    time: str
    path: str
    priority: str = 'normal'

class WeeklyTrendItem(BaseModel):
    day: str
    value: int
    
class TeacherDashboardOut(BaseModel):
    stats: TeacherStatsOut
    todos: List[TodoItem]

class ClassAnalysisOut(BaseModel):
    class_id: int
    class_name: str
    student_count: int
    avg_distance: float
    avg_duration: int
    completion_rate: float


# Course Schemas (Phase 4.2 Enhanced)
class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None
    cover_url: Optional[str] = None  # 修改为 cover_url
    category: Optional[str] = None
    is_public: bool = True

class CourseCreate(CourseBase):
    pass

class CourseOut(CourseBase):
    id: int
    teacher_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class CourseContentBase(BaseModel):
    title: str
    content_type: str
    content_url: Optional[str] = None
    duration: Optional[int] = None
    order: int = 0

class CourseContentCreate(CourseContentBase):
    pass

class CourseContentOut(CourseContentBase):
    id: int
    course_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class EnrollmentCreate(BaseModel):
    course_id: int

class EnrollmentOut(BaseModel):
    id: int
    student_id: int
    course_id: int
    joined_at: datetime  # 修改为 joined_at 以匹配数据库
    status: str
    
    class Config:
        from_attributes = True

class CourseProgressUpdate(BaseModel):
    content_id: int
    progress: float
    last_position: Optional[int] = None

class CourseProgressOut(BaseModel):
    id: int
    student_id: int
    content_id: int
    progress: float
    completed: bool
    last_position: int
    updated_at: datetime
    
    class Config:
        from_attributes = True

class CourseDetailOut(CourseOut):
    contents: List[CourseContentOut] = []
    enrolled: bool = False  # 当前用户是否已选课
    enrollment_count: int = 0  # 选课人数

class CourseListResponse(BaseModel):
    items: List[CourseOut]
    total: int
    page: int
    size: int

# Approval Schemas
class ApprovalItemOut(BaseModel):
    id: int
    student_name: str
    type: str
    reason: str
    created_at: str

class ApprovalActionOut(BaseModel):
    success: bool
    message: str



# Run Group Schemas
class RunGroupBase(BaseModel):
    name: str
    description: Optional[str] = None
    avatar: Optional[str] = None


class RunGroupCreate(RunGroupBase):
    pass


class RunGroupOut(RunGroupBase):
    id: int
    creator_id: int
    total_mileage: float
    member_count: int
    rank: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RunGroupDetailOut(RunGroupOut):
    month_activity_count: int = 0  # 本月活动数（动态计算）


class RunGroupMemberOut(BaseModel):
    id: int
    user_id: int
    user_name: str
    role: str
    total_mileage: float
    joined_at: datetime

    class Config:
        from_attributes = True


class RunGroupActivityBase(BaseModel):
    title: str
    description: Optional[str] = None
    activity_time: datetime
    location: Optional[str] = None
    distance: Optional[float] = None
    total_quota: int = 100


class RunGroupActivityCreate(RunGroupActivityBase):
    group_id: int


class RunGroupActivityOut(RunGroupActivityBase):
    id: int
    group_id: int
    apply_count: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class RunGroupActivityListResponse(BaseModel):
    items: List[RunGroupActivityOut]
    total: int
    page: int
    size: int


class RunGroupRankOut(BaseModel):
    group_id: int
    group_name: str
    total_mileage: float
    rank: int
    member_count: int

    class Config:
        from_attributes = True


# 阳光跑班级排行 Schemas
class ClassMemberSunshineItem(BaseModel):
    user_id: int
    student_id: str
    name: str
    class_name: str
    weekly_count: int
    total_score: int


class ClassMemberSunshineList(BaseModel):
    items: List[ClassMemberSunshineItem]
