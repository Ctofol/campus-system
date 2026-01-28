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

class TokenData(BaseModel):
    phone: str | None = None
    role: str | None = None

# Metrics & Evidence
class ActivityMetricsCreate(BaseModel):
    distance: Optional[float] = None
    duration: int
    pace: Optional[str] = None
    count: Optional[int] = None
    qualified: bool = False

class ActivityEvidenceCreate(BaseModel):
    evidence_type: str
    data_ref: str

class ActivityMetricsOut(ActivityMetricsCreate):
    id: int
    activity_id: int
    class Config:
        orm_mode = True

class ActivityEvidenceOut(ActivityEvidenceCreate):
    id: int
    activity_id: int
    class Config:
        orm_mode = True

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
        orm_mode = True

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
        orm_mode = True

# Teacher
class ApproveRequest(BaseModel):
    result: str = "approved"

class TeacherActivityListOut(ActivityOut):
    student_name: str

    class Config:
        orm_mode = True

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

class TaskOut(TaskCreate):
    id: int
    created_by: int
    
    class Config:
        orm_mode = True

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
    student_statuses: List[StudentCompletionStatus]

class TaskListStats(TaskOut):
    total_students: int
    completed_count: int
