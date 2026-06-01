"""
视频评分服务：体测分析结果写入 metrics。
"""
import json
from typing import Optional, Tuple

from .. import models


def apply_analysis_to_metrics(
    metrics: models.ActivityMetrics,
    count: int,
    qualified: bool,
    score: int,
    score_detail: str,
    *,
    success: bool = True,
) -> None:
    metrics.count = count
    metrics.qualified = qualified
    metrics.score = score
    metrics.score_detail = score_detail
    metrics.analysis_status = "success" if success else "failed"
    metrics.analysis_error = None if success else (score_detail or "分析失败")


def init_pending_metrics(metrics: models.ActivityMetrics, exercise_type: Optional[str] = None) -> None:
    metrics.exercise_type = exercise_type
    metrics.count = 0
    metrics.qualified = False
    metrics.score = None
    metrics.score_detail = None
    metrics.analysis_status = "pending"
    metrics.analysis_error = None


def get_video_score(video_url: str, exercise_type: Optional[str] = None) -> Tuple[int, str]:
    """同步分析入口（供重分析接口）。"""
    from .pose_analyzer import analyze_test_video

    count, qualified, score, detail = analyze_test_video(video_url, exercise_type)
    return score, detail
