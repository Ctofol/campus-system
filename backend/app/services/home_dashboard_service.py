"""学生首页 Dashboard 数据聚合。"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from .. import models

CN_TZ = timezone(timedelta(hours=8))


def _week_start_cn(now: Optional[datetime] = None) -> datetime:
    now = now or datetime.now(CN_TZ)
    day = now.weekday()  # Mon=0
    start = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=day)
    return start


def _to_cn(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(CN_TZ)


def _normalize_distance_km(raw: Any) -> float:
    d = float(raw or 0)
    if d <= 0:
        return 0.0
    return d / 1000.0 if d > 100 else d


def _format_duration_hms(sec: int) -> str:
    s = max(0, int(sec or 0))
    h = s // 3600
    m = (s % 3600) // 60
    ss = s % 60
    pad = lambda n: str(n).zfill(2)
    return f"{h}:{pad(m)}:{pad(ss)}" if h > 0 else f"{m}:{pad(ss)}"


def _format_pace(pace_min_per_km: float) -> str:
    if not pace_min_per_km or pace_min_per_km <= 0 or pace_min_per_km >= 999:
        return "--'--\""
    total_sec = int(round(pace_min_per_km * 60))
    mm = total_sec // 60
    ss = total_sec % 60
    return f"{mm}'{str(ss).zfill(2)}\""


def _pace_from_metrics(metrics: Optional[models.ActivityMetrics]) -> float:
    if not metrics:
        return 0.0
    try:
        pace = float(metrics.pace) if metrics.pace is not None else 0.0
    except (TypeError, ValueError):
        pace = 0.0
    if 0 < pace < 999:
        return pace
    km = _normalize_distance_km(metrics.distance)
    sec = int(metrics.duration or 0)
    if km > 0 and sec > 0:
        return sec / 60.0 / km
    return 0.0


def _parse_trajectory_points(raw: Any) -> List[Dict[str, float]]:
    if raw is None:
        return []
    try:
        arr = json.loads(raw) if isinstance(raw, str) else raw
    except (json.JSONDecodeError, TypeError):
        return []
    if not isinstance(arr, list):
        return []
    out: List[Dict[str, float]] = []
    for p in arr:
        if not isinstance(p, dict):
            continue
        lat = p.get("latitude", p.get("lat"))
        lng = p.get("longitude", p.get("lng", p.get("lon")))
        try:
            lat_f, lng_f = float(lat), float(lng)
        except (TypeError, ValueError):
            continue
        if abs(lat_f) <= 90 and abs(lng_f) <= 180:
            out.append({"lat": lat_f, "lng": lng_f})
    return out


def _trajectory_preview(points: List[Dict[str, float]], max_pts: int = 24) -> List[Dict[str, float]]:
    if len(points) < 2:
        return []
    if len(points) <= max_pts:
        return points
    step = max(1, len(points) // max_pts)
    sampled = points[::step]
    if sampled[-1] != points[-1]:
        sampled.append(points[-1])
    return sampled[:max_pts]


def _is_free_run(act: models.Activity) -> bool:
    return (
        act.type == "run"
        and act.task_id is None
        and (act.source or "free") != "task"
    )


def _is_sunshine_valid(act: models.Activity) -> bool:
    return _is_free_run(act) and act.is_valid is True


def _format_recent_time(dt: datetime) -> str:
    if not dt:
        return ""
    local = dt.replace(tzinfo=timezone.utc).astimezone(CN_TZ) if dt.tzinfo is None else dt.astimezone(CN_TZ)
    return f"{local.month:02d}/{local.day:02d} {local.hour:02d}:{local.minute:02d}"


def _activity_to_detail_dict(act: models.Activity) -> Dict[str, Any]:
    """供小程序 history/detail 使用的精简活动对象（含轨迹）。"""
    metrics = act.metrics
    traj_raw = metrics.trajectory if metrics else None
    points = _parse_trajectory_points(traj_raw)
    metrics_out: Dict[str, Any] = {}
    if metrics:
        metrics_out = {
            "distance": metrics.distance,
            "duration": metrics.duration,
            "pace": metrics.pace,
            "trajectory": traj_raw,
            "calories": getattr(metrics, "calories", None),
            "step_count": metrics.step_count,
        }
    return {
        "id": act.id,
        "type": act.type,
        "source": act.source,
        "status": act.status,
        "started_at": act.started_at.isoformat() if act.started_at else None,
        "ended_at": act.ended_at.isoformat() if act.ended_at else None,
        "is_valid": act.is_valid,
        "fail_reason": act.fail_reason,
        "task_id": act.task_id,
        "metrics": metrics_out,
        "has_trajectory": len(points) >= 2,
    }


def get_total_distance_km(user_id: int, db: Session) -> float:
    rows = (
        db.query(models.ActivityMetrics.distance)
        .join(models.Activity, models.ActivityMetrics.activity_id == models.Activity.id)
        .filter(
            models.Activity.user_id == user_id,
            models.Activity.type == "run",
        )
        .all()
    )
    total = sum(_normalize_distance_km(r[0]) for r in rows)
    return round(total, 1)


def aggregate_weekly_runs(activities: List[models.Activity]) -> Dict[str, Any]:
    week_start = _week_start_cn()
    week_runs = [
        a
        for a in activities
        if _is_free_run(a)
        and a.started_at
        and _to_cn(a.started_at) >= week_start
    ]

    dist_km = 0.0
    dur_sec = 0
    calories = 0.0
    pace_weighted = 0.0
    sunshine_km = 0.0

    for act in week_runs:
        m = act.metrics
        if not m:
            continue
        km = _normalize_distance_km(m.distance)
        dist_km += km
        dur_sec += int(m.duration or 0)
        cal = getattr(m, "calories", None)
        calories += float(cal) if cal else km * 60
        pace = _pace_from_metrics(m)
        if pace > 0 and km > 0:
            pace_weighted += pace * km
        if _is_sunshine_valid(act):
            sunshine_km += km

    pace_label = "--'--\""
    if dist_km > 0 and pace_weighted > 0:
        pace_label = _format_pace(pace_weighted / dist_km)
    elif dist_km > 0 and dur_sec > 0:
        pace_label = _format_pace(dur_sec / 60.0 / dist_km)

    return {
        "distance_km": f"{dist_km:.2f}",
        "duration_label": _format_duration_hms(dur_sec),
        "pace_label": pace_label,
        "calories": int(round(calories)),
        "run_count": len(week_runs),
        "sunshine_km": f"{sunshine_km:.2f}",
        "has_data": len(week_runs) > 0,
    }


def build_recent_runs(activities: List[models.Activity], limit: int = 3) -> List[Dict[str, Any]]:
    free_runs = [a for a in activities if _is_free_run(a)]
    free_runs.sort(key=lambda a: a.started_at or datetime.min, reverse=True)
    out: List[Dict[str, Any]] = []
    for act in free_runs[:limit]:
        m = act.metrics
        km = _normalize_distance_km(m.distance if m else 0)
        pace = _format_pace(_pace_from_metrics(m))
        points = _parse_trajectory_points(m.trajectory if m else None)
        has_track = len(points) >= 2
        out.append(
            {
                "id": act.id,
                "title": "自由跑",
                "distance_km": f"{km:.2f}",
                "time_label": _format_recent_time(act.started_at),
                "pace_label": f"{pace}/km" if pace != "--'--\"" else pace,
                "has_track": has_track,
                "is_valid": act.is_valid is True,
                "trajectory_preview": _trajectory_preview(points) if has_track else [],
                "activity": _activity_to_detail_dict(act),
            }
        )
    return out


def enrich_activity_trajectory_fields(act: models.Activity) -> Dict[str, Any]:
    m = act.metrics
    points = _parse_trajectory_points(m.trajectory if m else None)
    has_track = len(points) >= 2
    return {
        "has_trajectory": has_track,
        "trajectory_preview": _trajectory_preview(points) if has_track else [],
    }


def get_home_dashboard(user: models.User, db: Session) -> Dict[str, Any]:
    if user.role != "student":
        raise ValueError("not_student")

    activities = (
        db.query(models.Activity)
        .options(joinedload(models.Activity.metrics))
        .filter(models.Activity.user_id == user.id)
        .order_by(models.Activity.started_at.desc())
        .limit(80)
        .all()
    )

    unread = (
        db.query(func.count(models.UserNotification.id))
        .filter(
            models.UserNotification.user_id == user.id,
            models.UserNotification.is_read.is_(False),
        )
        .scalar()
        or 0
    )

    goal = float(user.weekly_run_goal_km or 0) if getattr(user, "weekly_run_goal_km", None) else 0.0

    return {
        "total_distance_km": f"{get_total_distance_km(user.id, db):.1f}",
        "weekly": aggregate_weekly_runs(activities),
        "recent_runs": build_recent_runs(activities),
        "weekly_run_goal_km": round(goal, 1) if goal > 0 else 0.0,
        "unread_notify_count": int(unread),
    }


def set_weekly_run_goal(user: models.User, km: float, db: Session) -> float:
    if km <= 0:
        user.weekly_run_goal_km = None
        db.commit()
        return 0.0
    val = round(min(999.0, float(km)), 1)
    user.weekly_run_goal_km = val
    db.commit()
    db.refresh(user)
    return val
