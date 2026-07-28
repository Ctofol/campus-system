"""
Video pose analysis for physical tests.

The public entry point keeps the old return shape:
    (count, qualified, score, score_detail_json)

Internally this is now a quality-gated pipeline:
1. MediaPipe Pose extracts landmarks.
2. Low-confidence / out-of-frame samples are ignored.
3. Per-exercise state machines count only full motion cycles.
4. score_detail explains confidence, quality and review reasons.
"""
from __future__ import annotations

import json
import math
import os
from collections import deque
from typing import Any, Deque, Dict, List, Optional, Tuple

from ... import config

_EXERCISE_ALIASES = {
    "pull-up": "pull_up",
    "pull_up": "pull_up",
    "sit-up": "sit_up",
    "sit_up": "sit_up",
    "push-up": "push_up",
    "push_up": "push_up",
}

_MIN_VISIBILITY = 0.45
_MIN_VALID_POSE_FRAMES = 8
_MIN_VALID_POSE_RATIO = 0.25
_SMOOTH_WINDOW = 5


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
    rel = ref.lstrip("/").replace("\\", "/")
    if rel.startswith("uploads/"):
        path = os.path.join(backend_root, rel)
    else:
        path = os.path.join(backend_root, "uploads", rel.replace("uploads/", ""))
    return path if os.path.isfile(path) else None


def _min_count_for(exercise_type: str, task_min_count: Optional[int] = None) -> int:
    if task_min_count and int(task_min_count) > 0:
        return int(task_min_count)
    return config.TEST_EXERCISE_MIN_COUNT.get(exercise_type, config.TEST_DEFAULT_MIN_COUNT)


def _landmark_index(mp_pose, name: str) -> int:
    return int(getattr(mp_pose.PoseLandmark, name).value)


def _point(lm, idx: int) -> Tuple[float, float]:
    p = lm[idx]
    return float(p.x), float(p.y)


def _visibility(lm, idx: int) -> float:
    return float(getattr(lm[idx], "visibility", 1.0) or 0.0)


def _avg(values: List[float]) -> Optional[float]:
    values = [v for v in values if v is not None]
    if not values:
        return None
    return sum(values) / len(values)


def _median(values: Deque[float]) -> Optional[float]:
    if not values:
        return None
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2


def _vec(p1: Tuple[float, float], p2: Tuple[float, float]) -> Tuple[float, float]:
    return p1[0] - p2[0], p1[1] - p2[1]


def _angle(a: Tuple[float, float], b: Tuple[float, float], c: Tuple[float, float]) -> float:
    ba = _vec(a, b)
    bc = _vec(c, b)
    denom = math.hypot(*ba) * math.hypot(*bc)
    if denom < 1e-6:
        return 180.0
    cosine = max(-1.0, min(1.0, (ba[0] * bc[0] + ba[1] * bc[1]) / denom))
    return math.degrees(math.acos(cosine))


def _required_landmarks(mp_pose, exercise_type: str) -> List[int]:
    common = [
        "LEFT_SHOULDER",
        "RIGHT_SHOULDER",
        "LEFT_HIP",
        "RIGHT_HIP",
    ]
    if exercise_type == "pull_up":
        names = ["NOSE", "LEFT_ELBOW", "RIGHT_ELBOW", "LEFT_WRIST", "RIGHT_WRIST", *common]
    elif exercise_type == "sit_up":
        names = ["LEFT_KNEE", "RIGHT_KNEE", *common]
    else:
        names = [
            "LEFT_ELBOW",
            "RIGHT_ELBOW",
            "LEFT_WRIST",
            "RIGHT_WRIST",
            "LEFT_ANKLE",
            "RIGHT_ANKLE",
            *common,
        ]
    return [_landmark_index(mp_pose, name) for name in names]


def _pose_quality(lm, indices: List[int]) -> Dict[str, Any]:
    vis = [_visibility(lm, idx) for idx in indices]
    xs = [float(lm[idx].x) for idx in indices]
    ys = [float(lm[idx].y) for idx in indices]
    in_frame = [0.0 <= x <= 1.0 and 0.0 <= y <= 1.0 for x, y in zip(xs, ys)]
    bbox_w = max(xs) - min(xs) if xs else 0.0
    bbox_h = max(ys) - min(ys) if ys else 0.0
    return {
        "min_visibility": round(min(vis), 3) if vis else 0.0,
        "avg_visibility": round(sum(vis) / len(vis), 3) if vis else 0.0,
        "in_frame_ratio": round(sum(1 for ok in in_frame if ok) / max(1, len(in_frame)), 3),
        "body_area": round(max(0.0, bbox_w * bbox_h), 3),
    }


def _valid_pose_sample(quality: Dict[str, Any]) -> bool:
    return (
        quality["min_visibility"] >= _MIN_VISIBILITY
        and quality["in_frame_ratio"] >= 0.9
        and quality["body_area"] >= 0.045
    )


def _side_elbow_angles(lm, mp_pose) -> List[float]:
    sides = []
    for side in ("LEFT", "RIGHT"):
        shoulder = _point(lm, _landmark_index(mp_pose, f"{side}_SHOULDER"))
        elbow = _point(lm, _landmark_index(mp_pose, f"{side}_ELBOW"))
        wrist = _point(lm, _landmark_index(mp_pose, f"{side}_WRIST"))
        sides.append(_angle(shoulder, elbow, wrist))
    return sides


def _body_line_error(lm, mp_pose) -> float:
    shoulder_y = _avg([
        _point(lm, _landmark_index(mp_pose, "LEFT_SHOULDER"))[1],
        _point(lm, _landmark_index(mp_pose, "RIGHT_SHOULDER"))[1],
    ]) or 0.0
    hip_y = _avg([
        _point(lm, _landmark_index(mp_pose, "LEFT_HIP"))[1],
        _point(lm, _landmark_index(mp_pose, "RIGHT_HIP"))[1],
    ]) or 0.0
    ankle_y = _avg([
        _point(lm, _landmark_index(mp_pose, "LEFT_ANKLE"))[1],
        _point(lm, _landmark_index(mp_pose, "RIGHT_ANKLE"))[1],
    ]) or 0.0
    expected_hip_y = (shoulder_y + ankle_y) / 2.0
    return abs(hip_y - expected_hip_y)


def _features(lm, mp_pose, exercise_type: str) -> Dict[str, float]:
    shoulder_y = _avg([
        _point(lm, _landmark_index(mp_pose, "LEFT_SHOULDER"))[1],
        _point(lm, _landmark_index(mp_pose, "RIGHT_SHOULDER"))[1],
    ]) or 0.0
    hip_y = _avg([
        _point(lm, _landmark_index(mp_pose, "LEFT_HIP"))[1],
        _point(lm, _landmark_index(mp_pose, "RIGHT_HIP"))[1],
    ]) or 0.0
    out: Dict[str, float] = {
        "shoulder_y": shoulder_y,
        "hip_y": hip_y,
        "shoulder_above_hip": hip_y - shoulder_y,
    }

    if exercise_type in ("pull_up", "push_up"):
        elbows = _side_elbow_angles(lm, mp_pose)
        out["elbow_angle"] = _avg(elbows) or 180.0
        out["left_elbow_angle"] = elbows[0]
        out["right_elbow_angle"] = elbows[1]

    if exercise_type == "pull_up":
        nose_y = _point(lm, _landmark_index(mp_pose, "NOSE"))[1]
        wrist_y = _avg([
            _point(lm, _landmark_index(mp_pose, "LEFT_WRIST"))[1],
            _point(lm, _landmark_index(mp_pose, "RIGHT_WRIST"))[1],
        ]) or 0.0
        out["nose_to_wrist_y"] = nose_y - wrist_y
    elif exercise_type == "push_up":
        out["body_line_error"] = _body_line_error(lm, mp_pose)
    else:
        knee_y = _avg([
            _point(lm, _landmark_index(mp_pose, "LEFT_KNEE"))[1],
            _point(lm, _landmark_index(mp_pose, "RIGHT_KNEE"))[1],
        ]) or 0.0
        out["hip_to_knee_y"] = knee_y - hip_y

    return out


class _RepCounter:
    def __init__(self, exercise_type: str):
        self.exercise_type = exercise_type
        self.stage = "unknown"
        self.count = 0
        self.partial_count = 0
        self.invalid_count = 0
        self.flags: List[str] = []

    def update(self, f: Dict[str, float]) -> None:
        if self.exercise_type == "pull_up":
            self._update_pull_up(f)
        elif self.exercise_type == "sit_up":
            self._update_sit_up(f)
        else:
            self._update_push_up(f)

    def _update_pull_up(self, f: Dict[str, float]) -> None:
        # Down: arms extended and face well below the hands.
        down = f["elbow_angle"] >= 145 and f["nose_to_wrist_y"] >= 0.12
        # Up: elbows bent and face reaches near hand/bar level.
        up = f["elbow_angle"] <= 115 and f["nose_to_wrist_y"] <= 0.08
        partial_up = f["elbow_angle"] <= 130 and f["nose_to_wrist_y"] <= 0.13

        if self.stage == "unknown" and down:
            self.stage = "down"
        elif self.stage == "down" and up:
            self.stage = "up"
        elif self.stage == "down" and partial_up:
            self.partial_count += 1
            self.stage = "partial_up"
        elif self.stage in ("up", "partial_up") and down:
            if self.stage == "up":
                self.count += 1
            else:
                self.invalid_count += 1
                self._flag("pull_up_range_too_small")
            self.stage = "down"

    def _update_sit_up(self, f: Dict[str, float]) -> None:
        # y grows downward. High torso means shoulders clearly above hips.
        up = f["shoulder_above_hip"] >= 0.14
        down = f["shoulder_above_hip"] <= 0.04
        partial_up = f["shoulder_above_hip"] >= 0.09

        if self.stage == "unknown" and down:
            self.stage = "down"
        elif self.stage == "down" and up:
            self.stage = "up"
        elif self.stage == "down" and partial_up:
            self.partial_count += 1
            self.stage = "partial_up"
        elif self.stage in ("up", "partial_up") and down:
            if self.stage == "up":
                self.count += 1
            else:
                self.invalid_count += 1
                self._flag("sit_up_range_too_small")
            self.stage = "down"

    def _update_push_up(self, f: Dict[str, float]) -> None:
        top = f["elbow_angle"] >= 150
        bottom = f["elbow_angle"] <= 95
        partial_bottom = f["elbow_angle"] <= 120
        body_line_ok = f.get("body_line_error", 0.0) <= 0.12

        if not body_line_ok:
            self._flag("push_up_body_line_unstable")

        if self.stage == "unknown" and top:
            self.stage = "top"
        elif self.stage == "top" and bottom:
            self.stage = "bottom" if body_line_ok else "invalid_bottom"
        elif self.stage == "top" and partial_bottom:
            self.partial_count += 1
            self.stage = "partial_bottom"
        elif self.stage in ("bottom", "invalid_bottom", "partial_bottom") and top:
            if self.stage == "bottom":
                self.count += 1
            else:
                self.invalid_count += 1
                if self.stage == "partial_bottom":
                    self._flag("push_up_depth_too_shallow")
            self.stage = "top"

    def _flag(self, value: str) -> None:
        if value not in self.flags:
            self.flags.append(value)


def _analyze_with_mediapipe(video_path: str, exercise_type: str) -> Optional[Dict[str, Any]]:
    try:
        import cv2
        import mediapipe as mp
    except ImportError:
        return None

    solutions = getattr(mp, "solutions", None)
    mp_pose = getattr(solutions, "pose", None) if solutions else None
    if mp_pose is None:
        return None

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {
            "engine": "mediapipe",
            "count": 0,
            "review_reason": "cannot_open_video",
            "risk_flags": ["cannot_open_video"],
        }

    frame_idx = 0
    sampled_frames = 0
    pose_frames = 0
    valid_pose_frames = 0
    low_quality_frames = 0
    sample_every = 2
    required = _required_landmarks(mp_pose, exercise_type)
    counter = _RepCounter(exercise_type)
    smooth: Dict[str, Deque[float]] = {}
    quality_samples: List[Dict[str, Any]] = []

    try:
        with mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            min_detection_confidence=0.55,
            min_tracking_confidence=0.5,
        ) as pose:
            while True:
                ok, frame = cap.read()
                if not ok:
                    break
                frame_idx += 1
                if frame_idx % sample_every != 0:
                    continue
                sampled_frames += 1

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                result = pose.process(rgb)
                if not result.pose_landmarks:
                    continue

                pose_frames += 1
                lm = result.pose_landmarks.landmark
                quality = _pose_quality(lm, required)
                quality_samples.append(quality)
                if not _valid_pose_sample(quality):
                    low_quality_frames += 1
                    continue

                valid_pose_frames += 1
                raw_features = _features(lm, mp_pose, exercise_type)
                smoothed_features: Dict[str, float] = {}
                for key, value in raw_features.items():
                    window = smooth.setdefault(key, deque(maxlen=_SMOOTH_WINDOW))
                    window.append(value)
                    smoothed_features[key] = _median(window) or value
                counter.update(smoothed_features)
    except Exception as exc:
        return {
            "engine": "mediapipe",
            "count": 0,
            "review_reason": "pose_analysis_exception",
            "risk_flags": ["pose_analysis_exception"],
            "error": str(exc)[:300],
        }
    finally:
        cap.release()

    valid_ratio = valid_pose_frames / max(1, sampled_frames)
    pose_ratio = pose_frames / max(1, sampled_frames)
    risk_flags = list(counter.flags)
    review_reason = None
    if pose_frames < _MIN_VALID_POSE_FRAMES:
        review_reason = "too_few_pose_frames"
        risk_flags.append("too_few_pose_frames")
    elif valid_pose_frames < _MIN_VALID_POSE_FRAMES or valid_ratio < _MIN_VALID_POSE_RATIO:
        review_reason = "pose_quality_too_low"
        risk_flags.append("pose_quality_too_low")
    elif counter.count == 0 and counter.partial_count > 0:
        review_reason = "only_partial_reps_detected"
        risk_flags.append("only_partial_reps_detected")

    avg_visibility = _avg([q["avg_visibility"] for q in quality_samples]) or 0.0
    avg_body_area = _avg([q["body_area"] for q in quality_samples]) or 0.0
    confidence = max(0.0, min(1.0, (valid_ratio * 0.55) + (pose_ratio * 0.25) + (avg_visibility * 0.20)))

    return {
        "engine": "mediapipe",
        "count": counter.count,
        "valid_reps": counter.count,
        "invalid_reps": counter.invalid_count,
        "partial_reps": counter.partial_count,
        "frames_total": frame_idx,
        "frames_sampled": sampled_frames,
        "pose_frames": pose_frames,
        "valid_pose_frames": valid_pose_frames,
        "low_quality_frames": low_quality_frames,
        "pose_ratio": round(pose_ratio, 3),
        "valid_pose_ratio": round(valid_ratio, 3),
        "confidence": round(confidence, 3),
        "quality": {
            "avg_visibility": round(avg_visibility, 3),
            "avg_body_area": round(avg_body_area, 3),
        },
        "review_reason": review_reason,
        "risk_flags": sorted(set(risk_flags)),
    }


def _score_for(count: int, min_need: int, confidence: float) -> int:
    if count <= 0:
        return 0
    if count >= min_need:
        base = 60 + max(0, count - min_need) * 4
    else:
        base = min(58, 30 + count * 3)
    # Low confidence should not silently award high scores.
    if confidence < 0.45:
        base = min(base, 55)
    return int(max(0, min(100, base)))


def _detail_json(data: Dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def analyze_test_video(
    video_url: str,
    exercise_type: Optional[str] = None,
    task_min_count: Optional[int] = None,
) -> Tuple[int, bool, int, str]:
    """
    Return (count, qualified, score, score_detail_json).
    """
    ex = _normalize_exercise(exercise_type)
    path = _resolve_video_path(video_url)
    min_need = _min_count_for(ex, task_min_count)

    if not path:
        detail = _detail_json(
            {
                "error": "video_not_found_local",
                "video_url": video_url,
                "engine": "mediapipe",
                "exercise_type": ex,
                "min_required": min_need,
                "count": 0,
                "qualified": False,
                "review_reason": "video_not_found_local",
                "risk_flags": ["video_not_found_local"],
            }
        )
        return 0, False, 0, detail

    raw = _analyze_with_mediapipe(path, ex)
    if raw is None:
        detail = _detail_json(
            {
                "engine": "mediapipe",
                "exercise_type": ex,
                "min_required": min_need,
                "count": 0,
                "qualified": False,
                "review_reason": "pose_engine_unavailable",
                "risk_flags": ["pose_engine_unavailable"],
            }
        )
        return 0, False, 0, detail

    count = int(raw.get("count") or 0)
    confidence = float(raw.get("confidence") or 0.0)
    review_reason = raw.get("review_reason")
    risk_flags = list(raw.get("risk_flags") or [])
    qualified = count >= min_need and not review_reason and confidence >= 0.45
    score = _score_for(count, min_need, confidence)

    detail = {
        "engine": raw.get("engine", "mediapipe"),
        "exercise_type": ex,
        "min_required": min_need,
        "count": count,
        "qualified": qualified,
        "score": score,
        "confidence": round(confidence, 3),
        "review_reason": review_reason,
        "risk_flags": risk_flags,
        **{k: v for k, v in raw.items() if k not in ("count", "engine", "confidence", "review_reason", "risk_flags")},
    }
    return count, qualified, score, _detail_json(detail)


def warmup_mediapipe_pose() -> str:
    try:
        import numpy as np
        import mediapipe as mp
    except ImportError as e:
        return f"mediapipe import failed: {e}"

    solutions = getattr(mp, "solutions", None)
    mp_pose = getattr(solutions, "pose", None) if solutions else None
    if mp_pose is None:
        return "mediapipe.solutions.pose not available"

    dummy_frame = np.zeros((192, 192, 3), dtype=np.uint8)

    try:
        with mp_pose.Pose(
            static_image_mode=True,
            model_complexity=1,
            min_detection_confidence=0.55,
            min_tracking_confidence=0.5,
        ) as pose:
            pose.process(dummy_frame)
    except Exception as e:
        return f"mediapipe warmup exception: {e}"

    return "ok"
