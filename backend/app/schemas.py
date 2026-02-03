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

class UserProfile(BaseModel):
    id: int
    name: str
    phone: str
    role: str
    class_name: Optional[str] = None
    student_id: Optional[str] = None
    group_name: Optional[str] = None
    health_status: str
    
    class Config:
        from_attributes = True

class TokenData(BaseModel):
    phone: str | None = None
    role: str | None = None

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

    class Config:
        from_attributes = True

# Teacher
class ApproveRequest(BaseModel):
    result: str = "approved"

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
    avg_pace: str
    task_count: int
    compliance_rate: int
