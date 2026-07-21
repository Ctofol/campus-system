"""
Run face verification.

Local provider supports commercial-ready three-way comparison:
profile vs start, profile vs end, and start vs end.
"""
from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from sqlalchemy.orm import Session

from .. import config, models
from .face_profile_service import get_student_face_profile, resolve_local_media_path


@dataclass
class FaceVerifyOutcome:
    ok: bool
    reason: str
    face_verified: bool
    liveness_pass: Optional[bool]
    match_score: Optional[float]
    fail_code: Optional[str]
    detail: Optional[str] = None


def _read_image_b64(data_ref: str) -> Optional[str]:
    path = resolve_local_media_path(data_ref)
    if not path:
        return None
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except OSError:
        return None


def _tencent_liveness(image_b64: str) -> Tuple[bool, str]:
    try:
        from tencentcloud.common import credential
        from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
        from tencentcloud.iai.v20200303 import iai_client, models as tc_models
    except ImportError:
        return False, "SDK_NOT_INSTALLED"

    if not config.TENCENT_SECRET_ID or not config.TENCENT_SECRET_KEY:
        return False, "NO_CREDENTIALS"

    try:
        cred = credential.Credential(config.TENCENT_SECRET_ID, config.TENCENT_SECRET_KEY)
        client = iai_client.IaiClient(cred, config.TENCENT_REGION)
        req = tc_models.DetectLiveFaceAccurateRequest()
        req.Image = image_b64
        req.FaceModelVersion = "3.0"
        resp = client.DetectLiveFaceAccurate(req)
        score = float(getattr(resp, "Score", 0) or 0)
        is_live = bool(getattr(resp, "IsLiveness", False)) or score >= 80
        return is_live, ""
    except TencentCloudSDKException as e:
        return False, str(e.get_message() if hasattr(e, "get_message") else e)
    except Exception as e:
        return False, str(e)


def _tencent_compare(img_a_b64: str, img_b_b64: str) -> Tuple[Optional[float], str]:
    try:
        from tencentcloud.common import credential
        from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
        from tencentcloud.iai.v20200303 import iai_client, models as tc_models
    except ImportError:
        return None, "SDK_NOT_INSTALLED"

    if not config.TENCENT_SECRET_ID or not config.TENCENT_SECRET_KEY:
        return None, "NO_CREDENTIALS"

    try:
        cred = credential.Credential(config.TENCENT_SECRET_ID, config.TENCENT_SECRET_KEY)
        client = iai_client.IaiClient(cred, config.TENCENT_REGION)
        req = tc_models.CompareFaceRequest()
        req.ImageA = img_a_b64
        req.ImageB = img_b_b64
        req.FaceModelVersion = "3.0"
        resp = client.CompareFace(req)
        return float(getattr(resp, "Score", 0) or 0), ""
    except TencentCloudSDKException as e:
        return None, str(e.get_message() if hasattr(e, "get_message") else e)
    except Exception as e:
        return None, str(e)


def _extract_face_urls(evidence: list) -> Tuple[Optional[str], Optional[str]]:
    start_url = None
    end_url = None
    legacy = []
    for ev in evidence or []:
        et = getattr(ev, "evidence_type", None) or (ev.get("evidence_type") if isinstance(ev, dict) else None)
        ref = getattr(ev, "data_ref", None) or (ev.get("data_ref") if isinstance(ev, dict) else None)
        if et == "start_face":
            start_url = ref
        elif et == "end_face":
            end_url = ref
        elif et == "camera" and ref:
            legacy.append(ref)
    if not start_url and legacy:
        start_url = legacy[0]
    if not end_url and len(legacy) > 1:
        end_url = legacy[1]
    return start_url, end_url


def _detail_json(data: Dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def _verify_run_faces_local(start_url: str, end_url: str) -> FaceVerifyOutcome:
    from .face_local_insightface import compare_two_images, similarity_to_display_score

    start_path = resolve_local_media_path(start_url)
    end_path = resolve_local_media_path(end_url)
    if not start_path or not end_path:
        return FaceVerifyOutcome(
            ok=True,
            reason="",
            face_verified=True,
            liveness_pass=None,
            match_score=None,
            fail_code="LOCAL_SKIP_NO_FILE",
            detail=_detail_json({"mode": "legacy_two_photo", "risk_flags": ["local_file_missing"]}),
        )

    sim, err = compare_two_images(start_path, end_path)
    if sim is None:
        return FaceVerifyOutcome(
            ok=False,
            reason=f"Face verification failed: {err}",
            face_verified=False,
            liveness_pass=None,
            match_score=None,
            fail_code="LOCAL_DETECT_FAIL",
            detail=_detail_json({"mode": "legacy_two_photo", "error": err}),
        )

    display = similarity_to_display_score(sim)
    if sim < config.FACE_LOCAL_MIN_SIMILARITY:
        return FaceVerifyOutcome(
            ok=False,
            reason=f"Face verification failed: start/end photos are not the same person ({display})",
            face_verified=False,
            liveness_pass=None,
            match_score=display,
            fail_code="NOT_SAME_PERSON",
            detail=_detail_json({
                "mode": "legacy_two_photo",
                "start_end_similarity": round(sim, 4),
                "threshold": config.FACE_LOCAL_MIN_SIMILARITY,
                "risk_flags": ["start_end_low_similarity"],
            }),
        )

    return FaceVerifyOutcome(
        ok=True,
        reason="",
        face_verified=True,
        liveness_pass=None,
        match_score=display,
        fail_code=None,
        detail=_detail_json({
            "mode": "legacy_two_photo",
            "start_end_similarity": round(sim, 4),
            "threshold": config.FACE_LOCAL_MIN_SIMILARITY,
        }),
    )


def _verify_run_faces_with_profile(
    start_url: str,
    end_url: str,
    user: models.User,
    db: Session,
) -> FaceVerifyOutcome:
    from .face_local_insightface import (
        MODEL_VERSION,
        compare_embeddings,
        extract_verified_embedding,
        similarity_to_display_score,
    )
    from .face_profile_service import load_embedding

    start_path = resolve_local_media_path(start_url)
    end_path = resolve_local_media_path(end_url)
    if not start_path or not end_path:
        detail = {"mode": "profile_three_way", "risk_flags": ["local_file_missing"]}
        return FaceVerifyOutcome(False, "Face verification failed: local photos missing", False, None, None, "MISSING_PHOTO", _detail_json(detail))

    profile = get_student_face_profile(db, user.id)
    if not profile or profile.status != "verified":
        detail = {"mode": "profile_three_way", "risk_flags": ["face_profile_required"]}
        return FaceVerifyOutcome(False, "Student face profile is not verified", False, None, None, "FACE_PROFILE_REQUIRED", _detail_json(detail))

    profile_emb = load_embedding(profile)
    if profile_emb is None:
        detail = {"mode": "profile_three_way", "risk_flags": ["face_profile_invalid"]}
        return FaceVerifyOutcome(False, "Student face profile is invalid", False, None, None, "FACE_PROFILE_INVALID", _detail_json(detail))

    start = extract_verified_embedding(start_path)
    end = extract_verified_embedding(end_path)
    risk_flags = []
    detail: Dict[str, Any] = {
        "mode": "profile_three_way",
        "threshold": config.FACE_LOCAL_MIN_SIMILARITY,
        "model_version": MODEL_VERSION,
        "profile_image_url": profile.image_url,
    }
    if start.embedding is None:
        risk_flags.append("start_face_detect_failed")
        detail["start_error"] = start.error
        detail["start_quality"] = start.quality
    if end.embedding is None:
        risk_flags.append("end_face_detect_failed")
        detail["end_error"] = end.error
        detail["end_quality"] = end.quality
    if start.embedding is None or end.embedding is None:
        detail["risk_flags"] = risk_flags
        return FaceVerifyOutcome(False, "Face verification failed: cannot detect valid face", False, None, None, "LOCAL_DETECT_FAIL", _detail_json(detail))

    scores = {
        "profile_start_similarity": compare_embeddings(profile_emb, start.embedding),
        "profile_end_similarity": compare_embeddings(profile_emb, end.embedding),
        "start_end_similarity": compare_embeddings(start.embedding, end.embedding),
    }
    min_sim = min(scores.values())
    for key, value in scores.items():
        if value < config.FACE_LOCAL_MIN_SIMILARITY:
            risk_flags.append(f"{key}_low")

    detail.update({
        "similarities": {k: round(v, 4) for k, v in scores.items()},
        "scores": {k.replace("_similarity", "_score"): similarity_to_display_score(v) for k, v in scores.items()},
        "start_quality": start.quality,
        "end_quality": end.quality,
        "risk_flags": risk_flags,
    })
    display = similarity_to_display_score(min_sim)
    if risk_flags:
        return FaceVerifyOutcome(
            ok=False,
            reason=f"Face verification failed: three-way comparison below threshold ({display})",
            face_verified=False,
            liveness_pass=None,
            match_score=display,
            fail_code="NOT_SAME_PERSON",
            detail=_detail_json(detail),
        )

    return FaceVerifyOutcome(True, "", True, None, display, None, _detail_json(detail))


def verify_run_faces(evidence: list, user: Optional[models.User] = None, db: Optional[Session] = None) -> FaceVerifyOutcome:
    start_url, end_url = _extract_face_urls(evidence)

    if not start_url or not end_url:
        missing = []
        if not start_url:
            missing.append("start_face")
        if not end_url:
            missing.append("end_face")
        return FaceVerifyOutcome(
            ok=False,
            reason="Face verification failed: missing start/end face photos",
            face_verified=False,
            liveness_pass=False,
            match_score=None,
            fail_code="MISSING_PHOTO",
            detail=_detail_json({"missing": missing, "risk_flags": ["missing_photo"]}),
        )

    provider = (config.FACE_PROVIDER or "none").lower()
    if provider == "none":
        return FaceVerifyOutcome(True, "", True, None, None, None, _detail_json({"mode": "provider_none"}))

    if provider == "local":
        if user is not None and db is not None:
            return _verify_run_faces_with_profile(start_url, end_url, user, db)
        return _verify_run_faces_local(start_url, end_url)

    if provider != "tencent":
        return FaceVerifyOutcome(True, "", True, None, None, None, _detail_json({"mode": "unknown_provider_skip", "provider": provider}))

    start_b64 = _read_image_b64(start_url)
    end_b64 = _read_image_b64(end_url)
    if not start_b64 or not end_b64:
        return FaceVerifyOutcome(True, "", True, None, None, "PROVIDER_SKIP_LOCAL", _detail_json({"mode": "tencent", "risk_flags": ["local_file_missing"]}))

    live_start, err_s = _tencent_liveness(start_b64)
    if not live_start:
        msg = "Face verification failed: start photo liveness failed"
        if err_s:
            msg += f" ({err_s})"
        return FaceVerifyOutcome(False, msg, False, False, None, "LIVENESS_FAIL", _detail_json({"mode": "tencent", "start_liveness_error": err_s}))

    live_end, err_e = _tencent_liveness(end_b64)
    if not live_end:
        msg = "Face verification failed: end photo liveness failed"
        if err_e:
            msg += f" ({err_e})"
        return FaceVerifyOutcome(False, msg, False, False, None, "LIVENESS_FAIL", _detail_json({"mode": "tencent", "end_liveness_error": err_e}))

    score, err_c = _tencent_compare(start_b64, end_b64)
    if score is None:
        return FaceVerifyOutcome(True, "", True, True, None, "COMPARE_UNAVAILABLE", _detail_json({"mode": "tencent", "compare_error": err_c}))

    if score < config.FACE_MATCH_THRESHOLD:
        return FaceVerifyOutcome(
            False,
            f"Face verification failed: start/end photos are not the same person ({score:.1f})",
            False,
            True,
            score,
            "NOT_SAME_PERSON",
            _detail_json({"mode": "tencent", "score": score, "threshold": config.FACE_MATCH_THRESHOLD}),
        )

    return FaceVerifyOutcome(True, "", True, True, score, None, _detail_json({"mode": "tencent", "score": score}))


def apply_face_outcome_to_activity(activity, outcome: FaceVerifyOutcome) -> None:
    activity.face_verified = outcome.face_verified
    activity.face_liveness_pass = outcome.liveness_pass
    activity.face_match_score = outcome.match_score
    activity.face_fail_code = outcome.fail_code
    if hasattr(activity, "face_detail"):
        activity.face_detail = outcome.detail
