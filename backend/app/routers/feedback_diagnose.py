from fastapi import APIRouter
from pydantic import BaseModel, Field

from ..services.feedback_diagnosis import diagnose_feedback

router = APIRouter(prefix="/feedback", tags=["feedback"])


class FeedbackIn(BaseModel):
    feedback: str = Field(..., min_length=1, description="用户反馈原文")
    prefer_llm: bool = Field(True, description="若服务端配置了 LLM 密钥则优先走模型")


class DiagnosisOut(BaseModel):
    original_feedback: str
    category: str
    severity: str
    diagnosis: str
    suggested_action: str


@router.post("/diagnose", response_model=DiagnosisOut)
async def post_diagnose(body: FeedbackIn) -> DiagnosisOut:
    """
    智能反馈诊断：分类 Network / Path / Permission / Logic，严重等级 P0–P3，
    并附带自愈联动建议。结果会追加写入 FEEDBACK_AUDIT_LOG 或 FEEDBACK_LOG_DIR。
    """
    data = diagnose_feedback(body.feedback, prefer_llm=body.prefer_llm)
    return DiagnosisOut(**data)
