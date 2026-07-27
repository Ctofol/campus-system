"""
体测视频异步分析：后台线程更新 activity_metrics。
"""
from __future__ import annotations

import json
import logging
import threading

from sqlalchemy.orm import Session

from .. import database, models
from .face_profile_service import verify_profile_in_video
from .pose_analyzer import analyze_test_video
from .video_score import apply_analysis_to_metrics

logger = logging.getLogger(__name__)


def _merge_score_detail_with_identity(
    detail: str,
    identity: dict,
    review_reason: str | None = None,
) -> str:
    try:
        detail_obj = json.loads(detail or "{}")
    except Exception:
        detail_obj = {}
    if not isinstance(detail_obj, dict):
        detail_obj = {}

    risk_flags = set(detail_obj.get("risk_flags") or [])
    for flag in identity.get("risk_flags") or []:
        risk_flags.add(flag)
    if review_reason:
        detail_obj["review_reason"] = review_reason
        risk_flags.add(review_reason)

    detail_obj["identity"] = identity
    detail_obj["risk_flags"] = sorted(risk_flags)
    return json.dumps(detail_obj, ensure_ascii=False)


def _run_analysis_job(activity_id: int) -> None:
    db: Session = database.SessionLocal()
    try:
        act = db.query(models.Activity).filter(models.Activity.id == activity_id).first()
        if not act or not act.metrics:
            return
        metrics = act.metrics
        if not metrics.video_url:
            metrics.analysis_status = "failed"
            metrics.analysis_error = "缺少视频"
            db.commit()
            return

        metrics.analysis_status = "pending"
        db.commit()

        identity = verify_profile_in_video(db, act.user, metrics.video_url)
        identity_ok = bool(identity.get("ok"))
        act.face_verified = identity_ok
        act.face_match_score = identity.get("best_score")
        act.face_fail_code = identity.get("fail_code")
        if hasattr(act, "face_detail"):
            act.face_detail = json.dumps({"type": "test_identity", **identity}, ensure_ascii=False)

        task_min = None
        if act.task_id:
            task = db.query(models.Task).filter(models.Task.id == act.task_id).first()
            if task and task.min_count:
                task_min = int(task.min_count)

        try:
            count, qualified, score, detail = analyze_test_video(
                metrics.video_url,
                metrics.exercise_type,
                task_min,
            )
            apply_analysis_to_metrics(metrics, count, qualified, score, detail, success=True)
            try:
                detail_obj = json.loads(detail or "{}")
            except Exception:
                detail_obj = {}
            if not identity_ok:
                metrics.analysis_status = "needs_review"
                metrics.analysis_error = "视频身份校验未通过，需要老师复核"
                metrics.score_detail = _merge_score_detail_with_identity(
                    detail,
                    identity,
                    "test_identity_verification_failed",
                )
                act.is_valid = False
                act.fail_reason = "体测身份校验需教师复核"
                db.commit()
                return
            if detail_obj.get("review_reason") or detail_obj.get("risk_flags"):
                metrics.analysis_status = "needs_review"
                metrics.analysis_error = detail_obj.get("review_reason") or "pose analysis needs review"
                act.is_valid = False
                act.fail_reason = "体测动作识别需教师复核"
                db.commit()
                return
            if act.source == "task" and act.task_id and task_min:
                act.is_valid = count >= task_min
                act.fail_reason = None if act.is_valid else f"次数未达标（需≥{task_min}次，实际{count}次）"
            elif act.source == "free":
                act.is_valid = qualified
                act.fail_reason = None if qualified else "体测未达标"
        except Exception as e:
            logger.exception("test analysis failed activity_id=%s", activity_id)
            metrics.analysis_status = "failed"
            metrics.analysis_error = str(e)[:500]
            act.fail_reason = "视频分析失败，请重新提交或联系教师"
        db.commit()
    finally:
        db.close()


def enqueue_test_analysis(activity_id: int) -> None:
    if not activity_id:
        return
    t = threading.Thread(target=_run_analysis_job, args=(activity_id,), daemon=True)
    t.start()


def run_test_analysis_sync(activity_id: int) -> None:
    """同步执行（测试或无后台线程环境）。"""
    _run_analysis_job(activity_id)
