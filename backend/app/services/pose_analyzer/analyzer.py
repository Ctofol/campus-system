"""
体测视频姿态分析：优先 Mediapipe Pose，不可用时使用运动强度启发式（非随机）。
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional, Tuple

from ... import config

_EXERCISE_ALIASES = {
    "pull-up": "pull_up",
    "pull_up": "pull_up",
    "sit-up": "sit_up",
    "sit_up": "sit_up",
    "push-up": "push_up",
    "push_up": "push_up",
}


def _normalize_exercise(exercise_type: Optional[str]) -> str:
    if not exercise_type:
        return "pull_up"
    key = exercise_type.strip().lower().replace(" ", "_")
    return _EXERCISE_ALIASES.get(key, key if key in ("pull_up", "sit_up", "push_up") else "pull_up")


def _resolve_video_path(video_url: str) -> Optional[str]:
    if not video_url:
        return None
    ref = video_url.strip()
    if ref.startswith("http://") or ref.startswith("https://"):
        return None
    backend_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    rel = ref.lstrip("/")
    if rel.startswith("uploads/"):
        path = os.path.join(backend_root, rel)
    else:
        path = os.path.join(backend_root, "uploads", rel.replace("uploads/", ""))
    return path if os.path.isfile(path) else None


def _min_count_for(exercise_type: str, task_min_count: Optional[int] = None) -> int:
    if task_min_count and int(task_min_count) > 0:
        return int(task_min_count)
    return config.TEST_EXERCISE_MIN_COUNT.get(
        exercise_type, config.TEST_DEFAULT_MIN_COUNT
    )


def _analyze_with_mediapipe(video_path: str, exercise_type: str) -> Optional[Dict[str, Any]]:
    try:
        import cv2
        import mediapipe as mp
        import numpy as np
    except ImportError:
        return None

    solutions = getattr(mp, "solutions", None)
    mp_pose = getattr(solutions, "pose", None) if solutions else None
    if mp_pose is None:
        return None

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None

    reps = 0
    state = "down"
    frame_idx = 0
    pose_frames = 0
    sample_every = 2

    try:
        with mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5) as pose:
            while True:
                ok, frame = cap.read()
                if not ok:
                    break
                frame_idx += 1
                if frame_idx % sample_every != 0:
                    continue
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                result = pose.process(rgb)
                if not result.pose_landmarks:
                    continue
                pose_frames += 1
                lm = result.pose_landmarks.landmark
                if exercise_type == "pull_up":
                    nose_y = lm[mp_pose.PoseLandmark.NOSE].y
                    wrist_y = (lm[mp_pose.PoseLandmark.LEFT_WRIST].y + lm[mp_pose.PoseLandmark.RIGHT_WRIST].y) / 2
                    up = nose_y < wrist_y - 0.03
                elif exercise_type == "sit_up":
                    shoulder_y = (lm[mp_pose.PoseLandmark.LEFT_SHOULDER].y + lm[mp_pose.PoseLandmark.RIGHT_SHOULDER].y) / 2
                    hip_y = (lm[mp_pose.PoseLandmark.LEFT_HIP].y + lm[mp_pose.PoseLandmark.RIGHT_HIP].y) / 2
                    up = shoulder_y < hip_y - 0.05
                else:
                    elbow_ang = _elbow_angle(lm, mp_pose)
                    up = elbow_ang < 90

                if up and state == "down":
                    state = "up"
                elif not up and state == "up":
                    state = "down"
                    reps += 1
    except Exception:
        return None
    finally:
        cap.release()

    return {
        "count": max(0, reps),
        "engine": "mediapipe",
        "frames_sampled": frame_idx,
        "pose_frames": pose_frames,
    }


def _elbow_angle(lm, mp_pose) -> float:
    import math

    def pt(idx):
        p = lm[idx]
        return (p.x, p.y)

    shoulder = pt(mp_pose.PoseLandmark.LEFT_SHOULDER)
    elbow = pt(mp_pose.PoseLandmark.LEFT_ELBOW)
    wrist = pt(mp_pose.PoseLandmark.LEFT_WRIST)
    a = _vec(shoulder, elbow)
    b = _vec(wrist, elbow)
    cos = max(-1.0, min(1.0, (a[0] * b[0] + a[1] * b[1]) / (math.hypot(*a) * math.hypot(*b) + 1e-6)))
    return math.degrees(math.acos(cos))


def _vec(p1, p2):
    return (p1[0] - p2[0], p1[1] - p2[1])


def _analyze_motion_heuristic(video_path: str, exercise_type: str) -> Dict[str, Any]:
    """无 Pose 库时：根据帧间差异估算次数（仍优于 random）。"""
    try:
        import cv2
    except ImportError:
        duration_guess = 30
        return {
            "count": max(1, duration_guess // 4),
            "engine": "fallback_time",
            "note": "opencv_unavailable",
        }

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {"count": 0, "engine": "fallback_failed", "note": "cannot_open_video"}

    fps = cap.get(cv2.CAP_PROP_FPS) or 15
    prev = None
    peaks = 0
    state = False
    frame_idx = 0

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frame_idx += 1
        if frame_idx % 3 != 0:
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        small = cv2.resize(gray, (160, 90))
        if prev is not None:
            diff = cv2.absdiff(small, prev).mean()
            active = diff > 8.0
            if active and not state:
                state = True
            elif not active and state:
                state = False
                peaks += 1
        prev = small

    cap.release()
    duration_sec = frame_idx / max(fps, 1)
    # 运动峰值过少时按时长保守估计
    if peaks < 2 and duration_sec > 5:
        peaks = max(peaks, int(duration_sec / 3))

    return {
        "count": max(0, peaks),
        "engine": "motion_heuristic",
        "duration_sec": round(duration_sec, 1),
        "exercise_type": exercise_type,
    }


def analyze_test_video(
    video_url: str,
    exercise_type: Optional[str] = None,
    task_min_count: Optional[int] = None,
) -> Tuple[int, bool, int, str]:
    """
    返回 (count, qualified, score, score_detail_json)
    """
    ex = _normalize_exercise(exercise_type)
    path = _resolve_video_path(video_url)
    min_need = _min_count_for(ex, task_min_count)

    if not path:
        detail = json.dumps(
            {"error": "video_not_found_local", "video_url": video_url},
            ensure_ascii=False,
        )
        return 0, False, 0, detail

    raw = _analyze_with_mediapipe(path, ex)
    if raw is None:
        detail = json.dumps(
            {
                "engine": "mediapipe",
                "exercise_type": ex,
                "min_required": min_need,
                "count": 0,
                "qualified": False,
                "review_reason": "pose_engine_unavailable",
                "risk_flags": ["pose_engine_unavailable"],
            },
            ensure_ascii=False,
        )
        return 0, False, 0, detail

    if int(raw.get("pose_frames") or 0) < 5:
        detail = json.dumps(
            {
                "engine": raw.get("engine"),
                "exercise_type": ex,
                "min_required": min_need,
                "count": 0,
                "qualified": False,
                "frames_sampled": raw.get("frames_sampled"),
                "pose_frames": raw.get("pose_frames"),
                "review_reason": "too_few_pose_frames",
                "risk_flags": ["too_few_pose_frames"],
            },
            ensure_ascii=False,
        )
        return 0, False, 0, detail

    count = int(raw.get("count", 0))
    qualified = count >= min_need
    score = min(100, 50 + count * 3) if qualified else min(60, 30 + count * 2)
    detail = json.dumps(
        {
            "engine": raw.get("engine"),
            "exercise_type": ex,
            "min_required": min_need,
            "count": count,
            "qualified": qualified,
            **{k: v for k, v in raw.items() if k not in ("count",)},
        },
        ensure_ascii=False,
    )
    return count, qualified, score, detail
