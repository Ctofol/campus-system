from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .. import auth, models
from ..database import get_db
from ..services.ai_assistant_service import (
    campus_qa,
    build_run_report,
    build_teacher_briefing,
    build_test_feedback,
    get_ai_status,
)

router = APIRouter(prefix="/ai-assistant", tags=["ai-assistant"])


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)


class RunReportRequest(BaseModel):
    activity_id: Optional[int] = None
    distance_km: Optional[float] = None
    duration_sec: Optional[int] = None
    pace: Optional[str] = None
    qualified: Optional[bool] = None


class TestFeedbackRequest(BaseModel):
    activity_id: Optional[int] = None
    project: Optional[str] = None
    exercise_type: Optional[str] = None
    count: Optional[int] = None
    score: Optional[int] = None
    qualified: Optional[bool] = None


@router.get("/status")
def ai_status():
    return get_ai_status()


@router.post("/chat")
def chat(
    payload: ChatRequest,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    return campus_qa(db, current_user, payload.question)


@router.post("/student/run-report")
def student_run_report(
    payload: RunReportRequest,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can generate run reports")
    return build_run_report(db, current_user, payload.activity_id, payload.dict())


@router.post("/student/test-feedback")
def student_test_feedback(
    payload: TestFeedbackRequest,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can generate test feedback")
    return build_test_feedback(db, current_user, payload.dict())


@router.get("/teacher/briefing")
def teacher_briefing(
    current_user: models.User = Depends(auth.get_current_teacher),
    db: Session = Depends(get_db),
):
    return build_teacher_briefing(db, current_user)
