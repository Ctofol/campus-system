from datetime import datetime, date, timedelta
from typing import Tuple
import random

from .. import models


def verify_activity(user: models.User, activity: models.Activity, db) -> Tuple[bool, str, bool]:
    """
    阳光跑自动审核逻辑：
    - 性别 + 里程：男生 < 2.0km / 女生 < 1.2km 视为无效
    - 配速区间：3:00 - 10:00 min/km（以分钟/公里的浮点数表示）
    - 频次限制：同一天内已有一条达标记录，则本次无效
    - 人脸验证：90% 通过率
    返回 (is_valid, fail_reason, face_verified)
    """
    metrics = activity.metrics
    if not metrics:
        return False, "缺少运动数据", False

    distance_km = metrics.distance or 0.0

    # pace 以字符串形式存储，例如 "5.2" 分/公里
    try:
        pace_val = float(metrics.pace) if metrics.pace is not None else None
    except ValueError:
        pace_val = None

    # 1. 性别 + 里程校验
    gender = (user.gender or "male").lower()
    min_distance = 2.0 if gender == "male" else 1.2
    if distance_km < min_distance:
        return False, "里程不足", False

    # 2. 配速区间校验（3 - 10 分钟/公里）
    if pace_val is None or pace_val < 3.0 or pace_val > 10.0:
        return False, "配速异常", False

    # 3. 频次限制：当天只允许一条达标记录
    today: date = datetime.utcnow().date()
    start = datetime(today.year, today.month, today.day)
    end = datetime(today.year, today.month, today.day, 23, 59, 59)

    valid_today_count = (
        db.query(models.Activity)
        .filter(
            models.Activity.user_id == user.id,
            models.Activity.type == "run",
            models.Activity.is_valid.is_(True),
            models.Activity.started_at >= start,
            models.Activity.started_at <= end,
        )
        .count()
    )
    if valid_today_count > 0:
        return False, "今日已达标", False

    # 4. 人脸验证：需要起跑+结束两张照片，并模拟 90% 通过率
    faces = [
        e for e in activity.evidence
        if e.evidence_type in ("start_face", "end_face", "camera")
    ]
    if len(faces) < 2:
        return False, "人脸验证失败", False

    face_verified = random.random() > 0.1
    if not face_verified:
        return False, "人脸验证失败", False

    return True, "", face_verified


def calculate_total_score(valid_count: int) -> int:
    """
    阶梯计分规则（学校最新标准）：
    - 0-10 次：0 分
    - 11-19 次：第 11 次为 42 分，此后每次 +2 分
    - 20 次：60 分（及格线）
    - 21-40 次：每次 +2 分，40 次为 100 分
    - >40 次：封顶 100 分
    """
    if valid_count <= 10:
        return 0
    if valid_count < 20:
        # 11 次为 42 分，每多 1 次 +2 分
        return 42 + (valid_count - 11) * 2
    if valid_count == 20:
        return 60

    # > 20
    score = 60 + (valid_count - 20) * 2
    return min(score, 100)


def get_sunshine_stats(user: models.User, db):
    """
    计算阳光跑看板和详情页所需数据：
    - total_valid_count: 历史达标次数
    - today_status: 'not_started' | 'success' | 'failed'
    - today_fail_reason: 最近一次失败原因（如有）
    - score / current_score: 阶梯计分
    - daily_records: 最近7天运动明细
    - user_gender: 学生性别
    """
    # 1. 历史达标次数
    total_valid_count = (
        db.query(models.Activity)
        .filter(
            models.Activity.user_id == user.id,
            models.Activity.type == "run",
            models.Activity.is_valid.is_(True),
        )
        .count()
    )

    score = calculate_total_score(total_valid_count)

    # 2. 今日状态
    today: date = datetime.utcnow().date()
    start = datetime(today.year, today.month, today.day)
    end = datetime(today.year, today.month, today.day, 23, 59, 59)

    today_activities = (
        db.query(models.Activity)
        .filter(
            models.Activity.user_id == user.id,
            models.Activity.type == "run",
            models.Activity.started_at >= start,
            models.Activity.started_at <= end,
        )
        .order_by(models.Activity.started_at.desc())
        .all()
    )

    today_status = "not_started"
    today_fail_reason = ""

    if today_activities:
        # 有任意一条达标则视为成功
        if any(a.is_valid for a in today_activities):
            today_status = "success"
        else:
            today_status = "failed"
            # 取最新一条的失败原因
            latest = today_activities[0]
            today_fail_reason = latest.fail_reason or ""

    # 3. 最近7天运动明细
    seven_days_ago: date = today - timedelta(days=6)
    seven_start = datetime(seven_days_ago.year, seven_days_ago.month, seven_days_ago.day)

    recent_activities = (
        db.query(models.Activity)
        .filter(
            models.Activity.user_id == user.id,
            models.Activity.type == "run",
            models.Activity.started_at >= seven_start,
        )
        .order_by(models.Activity.started_at.desc())
        .all()
    )

    daily_records = []
    for act in recent_activities:
        metrics = act.metrics
        if not metrics:
            continue
        daily_records.append({
            "started_at": act.started_at,
            "distance": metrics.distance or 0.0,
            "duration": metrics.duration or 0,
            "pace": metrics.pace,
            "is_valid": getattr(act, "is_valid", False),
            "fail_reason": getattr(act, "fail_reason", None),
        })

    return {
        "total_valid_count": total_valid_count,
        "score": score,
        "current_score": score,
        "today_status": today_status,
        "today_fail_reason": today_fail_reason,
        "daily_records": daily_records,
        "user_gender": (user.gender or "male").lower(),
    }


