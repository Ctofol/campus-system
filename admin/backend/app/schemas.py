from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UserLogin(BaseModel):
    phone: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    name: str

class ClassCreate(BaseModel):
    name: str

class ClassOut(BaseModel):
    id: int
    name: str
    teacher_id: Optional[int] = None
    student_count: int = 0
    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    phone: str
    name: str
    password: str
    role: str

class UserProfile(BaseModel):
    id: int
    name: str
    phone: str
    role: str
    class_name: Optional[str] = None
    student_id: Optional[str] = None
    created_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class DashboardStats(BaseModel):
    total_students: int
    total_teachers: int
    total_classes: int
    pending_approvals: int
