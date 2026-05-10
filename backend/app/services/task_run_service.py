"""任务跑步：与阳光跑（source=free 的自动核验）区分，按任务要求判定是否达标。"""
from __future__ import annotations

from datetime import datetime
from typing import Optional, Tuple

from sqlalchemy.orm import Session

from .. import models


def student_may_submit_task(student: models.User, task: models.Task) -> Tuple[bool, str]:
    if student.role != "student":
        return False, "仅学生可提交任务运动"
    now = datetime.utcnow()
    if task.starts_at and now < task.starts_at:
        return False, "任务尚未开始"
    if task.deadline and task.deadline < now:
        return False, "任务已截止"
    if task.class_id is not None and student.class_id != task.class_id:
        return False, "该任务不面向你所在班级"
    return True, ""


def evaluate_task_run(task: models.Task, metrics: models.ActivityMetrics) -> Tuple[bool, Optional[str]]:
    """
    跑步类任务达标判定（与阳光跑 verify_activity 无关）。
    - min_distance: 千米，与 metrics.distance 一致
    - min_duration: 秒，与 metrics.duration 一致
    """
    if task.type != "run":
        return True, None

    dist_km = metrics.distance if metrics.distance is not None else 0.0
    dur_sec = int(metrics.duration or 0)
    reasons = []

    if task.min_distance is not None and float(task.min_distance) > 0:
        if dist_km + 1e-9 < float(task.min_distance):
            reasons.append(f"距离未达标（需≥{float(task.min_distance):.2f}km，实际{dist_km:.2f}km）")

    if task.min_duration is not None and int(task.min_duration) > 0:
        if dur_sec < int(task.min_duration):
            need_min = int(task.min_duration) // 60
            need_sec = int(task.min_duration) % 60
            act_min = dur_sec // 60
            act_sec = dur_sec % 60
            reasons.append(
                f"时长未达标（需≥{need_min}分{need_sec}秒，实际{act_min}分{act_sec}秒）"
            )

    if reasons:
        return False, "；".join(reasons)
    return True, None
