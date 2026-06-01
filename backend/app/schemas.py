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
    # 瀛︾敓娉ㄥ唽涓撶敤锛氱敤浜庝笌 StudentProfile 杩涜妗ｆ鍖归厤
    student_id: str | None = None
    major_id: int | None = None
    class_id: int | None = None
    subject: str | None = None

class UserLogin(BaseModel):
    account: Optional[str] = None
    phone: Optional[str] = None
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    user_id: int
    name: str
    class_name: Optional[str] = None
    class_id: Optional[int] = None
    student_id: Optional[str] = None
    major: Optional[str] = None
    major_id: Optional[int] = None
    subject: Optional[str] = None

class UserProfile(BaseModel):
    id: int
    name: str
    phone: str
    role: str
    # class_name锛氬巻鍙插吋瀹癸紝甯镐负銆屼笓涓氬悕 + 鐝骇鍚嶃€嶆嫾鎺ワ紱绠＄悊绔〃鏍艰鐢?plain_class_name + major锛岄伩鍏嶉噸澶嶃€?    class_name: Optional[str] = None
    # plain_class_name锛氫粎琛屾斂鐝骇鍚?classes.name
    plain_class_name: Optional[str] = None
    class_id: Optional[int] = None
    student_id: Optional[str] = None
    major: Optional[str] = None
    major_id: Optional[int] = None
    subject: Optional[str] = None
    group_name: Optional[str] = None
    health_status: Optional[str] = "normal"
    signature: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    signature: Optional[str] = None
    avatar_url: Optional[str] = None

class TokenData(BaseModel):
    phone: str | None = None
    role: str | None = None

#
# Student Profile (妗ｆ婵€娲荤敤)
#

class StudentProfileBase(BaseModel):
    student_id: str
    full_name: str
    gender: str  # 'male' | 'female'
    class_name: str
    major: Optional[str] = None
    subject: Optional[str] = None


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
    major_id: int
    teacher_id: Optional[int] = None


class ClassTeacherUpdate(BaseModel):
    """Update class binding for a teacher."""

    teacher_id: Optional[int] = None


class ClassBind(BaseModel):
    class_ids: List[int]

class ClassOut(ClassBase):
    id: int
    major_id: int
    major_name: Optional[str] = None
    teacher_id: Optional[int] = None
    teacher_name: Optional[str] = None
    student_count: int = 0
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class MajorOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class SubjectOptionOut(BaseModel):
    id: int
    name: str
    sort_order: int = 0
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SubjectOptionCreate(BaseModel):
    name: str


class TeacherSubjectBase(BaseModel):
    subject_name: str

class TeacherSubjectOut(TeacherSubjectBase):
    id: int
    teacher_id: int
    enrollment_count: int = 0

    class Config:
        from_attributes = True


class TeacherBoundStudentsAdd(BaseModel):
    student_user_ids: List[int]


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
    trajectory: Optional[str] = None
    checkpoints: Optional[str] = None
    count: Optional[int] = None
    qualified: bool = False
    step_count: Optional[int] = None
    video_url: Optional[str] = None
    score: Optional[int] = None
    score_detail: Optional[str] = None
    exercise_type: Optional[str] = None
    analysis_status: Optional[str] = None
    analysis_error: Optional[str] = None

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
    task_id: Optional[int] = None  # 浠诲姟璺戞蹇呭～锛屼笌闃冲厜璺戝尯鍒?
class ActivityReviewOut(BaseModel):
    id: int
    teacher_id: int
    enrollment_count: int = 0
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
    # 鑷敱璺戯細闃冲厜璺戞牳楠岋紱浠诲姟璺戯細鏄惁婊¤冻浠诲姟瑕佹眰
    is_valid: Optional[bool] = None
    fail_reason: Optional[str] = None
    face_verified: Optional[bool] = None
    face_liveness_pass: Optional[bool] = None
    face_match_score: Optional[float] = None
    face_fail_code: Optional[str] = None
    today_completed: Optional[bool] = None
    task_id: Optional[int] = None
    task_title: Optional[str] = None
    task_completed: Optional[bool] = None  # 浠诲姟缁村害鏄惁杈炬爣锛堢瓑鍚屼换鍔′笅 is_valid锛?
    class Config:
        from_attributes = True


class ActivityFinishResponse(ActivityOut):
    """Response payload returned by activity settlement."""
    pass

# Teacher
class ApproveRequest(BaseModel):
    result: str = "approved"


class InvalidActivityOut(BaseModel):
    id: int
    user_id: Optional[int] = None
    student_name: str
    student_id: Optional[str] = None
    # 琛屾斂鐝骇鍚?classes.name锛沵ajor_name 涓轰笓涓?    class_name: Optional[str] = None
    major_name: Optional[str] = None
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
    starts_at: Optional[datetime] = None  # 鏈埌璇ユ椂闂村鐢熶笉鍙彁浜?    deadline: Optional[datetime] = None
    description: Optional[str] = None
    # 鏁欏笀鍙戝竷锛氭寚瀹?class_id 鍗曠彮锛屾垨 class_ids 澶氱彮锛堝悓涓€浠诲姟鍐呭澶嶅埗鍒板悇鐝級锛涗紭鍏堜娇鐢ㄩ潪绌虹殑 class_ids
    target_group: Optional[str] = "class"
    class_id: Optional[int] = None
    class_ids: Optional[List[int]] = None
    video_url: Optional[str] = None  # 浣撴祴浠诲姟瑙嗛URL锛堢浜岄樁娈垫柊澧烇級

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


class AdminStudentActivityItem(BaseModel):
    """Admin view of a single student exercise record."""

    id: int
    type: str
    record_kind: str
    source: Optional[str] = None
    started_at: datetime
    ended_at: datetime
    is_valid: bool
    fail_reason: Optional[str] = None
    distance_km: Optional[float] = None
    duration_sec: Optional[int] = None
    pace: Optional[str] = None
    task_id: Optional[int] = None
    task_title: Optional[str] = None


class AdminStudentActivitiesPage(BaseModel):
    items: List[AdminStudentActivityItem]
    total: int
    page: int
    size: int


class StudentCompletionStatus(BaseModel):
    student_id: int
    student_name: str
    status: str # 'completed', 'pending'
    completed_at: Optional[datetime] = None
    metric_value: Optional[str] = None # e.g. "2.5km" or "15 mins"
    activity_id: Optional[int] = None  # 绗笁闃舵鏂板锛氭椿鍔↖D锛岀敤浜庢墦鍒?    teacher_score: Optional[float] = None  # 绗笁闃舵鏂板锛氭暀甯堟墦鍒?
# 绗笁闃舵鏂板锛氭暀甯堟墦鍒嗙浉鍏硈chemas
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
    regular_score: float  # 骞虫椂鍒?    score_records: List[StudentScoreRecord]

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
    # 璇峰亣寮€濮?缁撴潫鏃堕棿锛堜粎 type == 'leave' 鏃跺繀濉級
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
    health_status: Optional[str] = "normal"
    abnormal_reason: Optional[str] = None
    group_name: Optional[str] = None
    health_requests: List[HealthRequestOut] = []
    # 鏁欏笀绔睍绀猴細琛屾斂鐝?/ 涓撲笟锛堜笌 User.plain_class_name銆乵ajor 瀵归綈锛?    plain_class_name: Optional[str] = None
    major_name: Optional[str] = None
    class_name: Optional[str] = None

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
    pending_health: int = 0  # 璇峰亣寰呭鐞嗘暟閲忥紙HealthRequest status=pending锛?    pending_activities: int = 0  # 杩愬姩寰呭鎵规暟閲忥紙Activity status=pending_review锛?    avg_pace: str
    task_count: int
    compliance_rate: int
    qualified_rate: int  # 杈炬爣鐜囷紙鐧惧垎鏁存暟锛?    completion_rate: int  # 瀹屾垚鐜囷紙鐧惧垎鏁存暟锛?
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
    # 琛屾斂鐝骇鍚嶏紱major_name 涓轰笓涓?    class_name: str
    major_name: Optional[str] = None
    student_count: int
    avg_distance: float
    avg_duration: int
    completion_rate: float


# Course Schemas (Phase 4.2 Enhanced)
class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None
    cover_url: Optional[str] = None  # 淇敼涓?cover_url
    category: Optional[str] = None
    is_public: bool = True

class CourseCreate(CourseBase):
    pass

class CourseOut(CourseBase):
    id: int
    teacher_id: int
    enrollment_count: int = 0
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
    joined_at: datetime  # 淇敼涓?joined_at 浠ュ尮閰嶆暟鎹簱
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
    enrolled: bool = False  # 褰撳墠鐢ㄦ埛鏄惁宸查€夎
    enrollment_count: int = 0  # 閫夎浜烘暟

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


class RunGroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    avatar: Optional[str] = None


class RunGroupOut(RunGroupBase):
    id: int
    creator_id: Optional[int] = None
    total_mileage: float
    member_count: int
    rank: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RunGroupDetailOut(RunGroupOut):
    month_activity_count: int = 0  # 鏈湀娲诲姩鏁帮紙鍔ㄦ€佽绠楋級


class RunGroupMembershipOut(RunGroupDetailOut):
    role: str = "member"


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


# 闃冲厜璺戠彮绾ф帓琛?Schemas
class ClassMemberSunshineItem(BaseModel):
    user_id: int
    student_id: str
    name: str
    class_name: str
    weekly_count: int
    total_score: int


class ClassMemberSunshineList(BaseModel):
    items: List[ClassMemberSunshineItem]

class StudentNotify(BaseModel):
    message: str


class UserNotificationOut(BaseModel):
    id: int
    title: str
    body: Optional[str] = None
    ntype: str = "system"
    is_read: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class UserNotificationUnread(BaseModel):
    count: int
