"""
Student face profile management and profile-based identity verification.
"""
from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Dict, Optional

import numpy as np
from sqlalchemy.orm import Session

from .. import config, models
from .face_local_insightface import (
    MODEL_VERSION,
    compare_embeddings,
    extract_verified_embedding,
    extract_verified_embedding_from_bgr,
    similarity_to_display_score,
)


def resolve_local_media_path(data_ref: str) -> Optional[str]:
    if not data_ref:
        return None
    ref = str(data_ref).strip()
    if ref.startswith("http://") or ref.startswith("https://"):
        return None
    backend_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    rel = ref.lstrip("/").replace("\\", "/")
    if rel.startswith("uploads/"):
        path = os.path.join(backend_root, rel)
    else:
        path = os.path.join(backend_root, "uploads", rel.replace("uploads/", ""))
    return path if os.path.isfile(path) else None


def _embedding_to_json(embedding: np.ndarray) -> str:
    return json.dumps([float(x) for x in embedding.flatten()], separators=(",", ":"))


def load_embedding(profile: models.StudentFaceProfile) -> Optional[np.ndarray]:
    try:
        data = json.loads(profile.embedding_json or "[]")
        if not data:
            return None
        return np.asarray(data, dtype=np.float32)
    except Exception:
        return None


def profile_to_status(profile: Optional[models.StudentFaceProfile]) -> Dict[str, Any]:
    if not profile:
        return {
            "status": "not_certified",
            "image_url": None,
            "updated_at": None,
            "model_version": None,
            "fail_reason": None,
            "quality_score": None,
        }
    return {
        "status": profile.status or "not_certified",
        "image_url": profile.image_url,
        "updated_at": profile.updated_at,
        "model_version": profile.model_version,
        "fail_reason": profile.fail_reason,
        "quality_score": profile.quality_score,
    }


def get_student_face_profile(db: Session, user_id: int) -> Optional[models.StudentFaceProfile]:
    return (
        db.query(models.StudentFaceProfile)
        .filter(models.StudentFaceProfile.user_id == user_id)
        .first()
    )


def upsert_student_face_profile(
    db: Session,
    user: models.User,
    image_url: str,
) -> models.StudentFaceProfile:
    image_path = resolve_local_media_path(image_url)
    if not image_path:
        raise ValueError("face image must be an uploaded local file")

    result = extract_verified_embedding(image_path)
    profile = get_student_face_profile(db, user.id)
    if not profile:
        profile = models.StudentFaceProfile(user_id=user.id, image_url=image_url, embedding_json="[]")
        db.add(profile)

    profile.image_url = image_url
    profile.model_version = MODEL_VERSION
    profile.updated_at = datetime.utcnow()
    profile.quality_score = (result.quality or {}).get("quality_score")

    if result.embedding is None:
        profile.status = "failed"
        profile.fail_reason = result.error or "face profile extraction failed"
        profile.embedding_json = "[]"
        db.commit()
        db.refresh(profile)
        raise ValueError(profile.fail_reason)

    profile.status = "verified"
    profile.fail_reason = None
    profile.embedding_json = _embedding_to_json(result.embedding)
    db.commit()
    db.refresh(profile)
    return profile


def compare_profile_to_image(
    profile: models.StudentFaceProfile,
    image_path: str,
) -> Dict[str, Any]:
    if not profile or profile.status != "verified":
        return {"ok": False, "fail_code": "FACE_PROFILE_REQUIRED", "reason": "student face profile not verified"}
    profile_embedding = load_embedding(profile)
    if profile_embedding is None:
        return {"ok": False, "fail_code": "FACE_PROFILE_INVALID", "reason": "student face profile embedding invalid"}

    result = extract_verified_embedding(image_path)
    if result.embedding is None:
        return {
            "ok": False,
            "fail_code": "FACE_DETECT_FAIL",
            "reason": result.error,
            "quality": result.quality,
        }

    sim = compare_embeddings(profile_embedding, result.embedding)
    return {
        "ok": sim >= config.FACE_LOCAL_MIN_SIMILARITY,
        "similarity": round(sim, 4),
        "score": similarity_to_display_score(sim),
        "threshold": config.FACE_LOCAL_MIN_SIMILARITY,
        "quality": result.quality,
        "fail_code": None if sim >= config.FACE_LOCAL_MIN_SIMILARITY else "NOT_PROFILE_OWNER",
        "reason": "" if sim >= config.FACE_LOCAL_MIN_SIMILARITY else "profile comparison below threshold",
    }


def verify_profile_in_video(
    db: Session,
    user: models.User,
    video_url: str,
    sample_count: int = 3,
) -> Dict[str, Any]:
    profile = get_student_face_profile(db, user.id)
    if not profile or profile.status != "verified":
        return {
            "ok": False,
            "fail_code": "FACE_PROFILE_REQUIRED",
            "reason": "student face profile not verified",
            "risk_flags": ["face_profile_required"],
        }

    profile_embedding = load_embedding(profile)
    if profile_embedding is None:
        return {
            "ok": False,
            "fail_code": "FACE_PROFILE_INVALID",
            "reason": "student face profile embedding invalid",
            "risk_flags": ["face_profile_invalid"],
        }

    path = resolve_local_media_path(video_url)
    if not path:
        return {
            "ok": False,
            "fail_code": "VIDEO_NOT_LOCAL",
            "reason": "video file is not available locally",
            "risk_flags": ["video_not_local"],
        }

    try:
        import cv2
    except ImportError:
        return {
            "ok": False,
            "fail_code": "OPENCV_UNAVAILABLE",
            "reason": "opencv is unavailable",
            "risk_flags": ["opencv_unavailable"],
        }

    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        return {
            "ok": False,
            "fail_code": "VIDEO_OPEN_FAILED",
            "reason": "cannot open video",
            "risk_flags": ["video_open_failed"],
        }

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    if total_frames <= 0:
        positions = [0]
    else:
        positions = [
            max(0, min(total_frames - 1, int(total_frames * ratio)))
            for ratio in (0.15, 0.5, 0.85)[: max(1, sample_count)]
        ]

    samples = []
    best = 0.0
    try:
        for pos in positions:
            cap.set(cv2.CAP_PROP_POS_FRAMES, pos)
            ok, frame = cap.read()
            if not ok:
                samples.append({"frame": pos, "ok": False, "reason": "frame_read_failed"})
                continue
            result = extract_verified_embedding_from_bgr(frame)
            if result.embedding is None:
                samples.append({
                    "frame": pos,
                    "ok": False,
                    "reason": result.error,
                    "quality": result.quality,
                })
                continue
            sim = compare_embeddings(profile_embedding, result.embedding)
            best = max(best, sim)
            samples.append({
                "frame": pos,
                "ok": sim >= config.FACE_LOCAL_MIN_SIMILARITY,
                "similarity": round(sim, 4),
                "score": similarity_to_display_score(sim),
                "quality": result.quality,
            })
    finally:
        cap.release()

    ok = best >= config.FACE_LOCAL_MIN_SIMILARITY
    return {
        "ok": ok,
        "best_similarity": round(best, 4),
        "best_score": similarity_to_display_score(best),
        "threshold": config.FACE_LOCAL_MIN_SIMILARITY,
        "samples": samples,
        "model_version": MODEL_VERSION,
        "fail_code": None if ok else "TEST_FACE_REVIEW",
        "reason": "" if ok else "no sampled frame matched the student face profile",
        "risk_flags": [] if ok else ["test_face_identity_low_confidence"],
    }
