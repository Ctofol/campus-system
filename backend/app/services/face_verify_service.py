"""
跑步起止人脸核验：活体检测 + 起止 1:1 同人比对。
未配置云厂商密钥时降级为「双照存在」采证模式。
"""
from __future__ import annotations

import base64
import os
from dataclasses import dataclass
from typing import List, Optional, Tuple

from .. import config


@dataclass
class FaceVerifyOutcome:
    ok: bool
    reason: str
    face_verified: bool
    liveness_pass: Optional[bool]
    match_score: Optional[float]
    fail_code: Optional[str]


def _resolve_local_path(data_ref: str) -> Optional[str]:
    if not data_ref:
        return None
    ref = data_ref.strip()
    if ref.startswith("http://") or ref.startswith("https://"):
        return None
    backend_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    rel = ref.lstrip("/")
    if rel.startswith("uploads/"):
        path = os.path.join(backend_root, rel)
    else:
        path = os.path.join(backend_root, "uploads", rel.replace("uploads/", ""))
    return path if os.path.isfile(path) else None


def _read_image_b64(data_ref: str) -> Optional[str]:
    path = _resolve_local_path(data_ref)
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
        from tencentcloud.iai.v20200303 import iai_client, models
    except ImportError:
        return False, "SDK_NOT_INSTALLED"

    if not config.TENCENT_SECRET_ID or not config.TENCENT_SECRET_KEY:
        return False, "NO_CREDENTIALS"

    try:
        cred = credential.Credential(config.TENCENT_SECRET_ID, config.TENCENT_SECRET_KEY)
        client = iai_client.IaiClient(cred, config.TENCENT_REGION)
        req = models.DetectLiveFaceAccurateRequest()
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
        from tencentcloud.iai.v20200303 import iai_client, models
    except ImportError:
        return None, "SDK_NOT_INSTALLED"

    if not config.TENCENT_SECRET_ID or not config.TENCENT_SECRET_KEY:
        return None, "NO_CREDENTIALS"

    try:
        cred = credential.Credential(config.TENCENT_SECRET_ID, config.TENCENT_SECRET_KEY)
        client = iai_client.IaiClient(cred, config.TENCENT_REGION)
        req = models.CompareFaceRequest()
        req.ImageA = img_a_b64
        req.ImageB = img_b_b64
        req.FaceModelVersion = "3.0"
        resp = client.CompareFace(req)
        score = float(getattr(resp, "Score", 0) or 0)
        return score, ""
    except TencentCloudSDKException as e:
        return None, str(e.get_message() if hasattr(e, "get_message") else e)
    except Exception as e:
        return None, str(e)


def _verify_run_faces_local(start_url: str, end_url: str) -> FaceVerifyOutcome:
    from .face_local_insightface import (
        compare_two_images,
        similarity_to_display_score,
    )

    start_path = _resolve_local_path(start_url)
    end_path = _resolve_local_path(end_url)
    if not start_path or not end_path:
        return FaceVerifyOutcome(
            ok=True,
            reason="",
            face_verified=True,
            liveness_pass=None,
            match_score=None,
            fail_code="LOCAL_SKIP_NO_FILE",
        )

    sim, err = compare_two_images(start_path, end_path)
    if sim is None:
        return FaceVerifyOutcome(
            ok=False,
            reason=f"人脸验证失败：{err}",
            face_verified=False,
            liveness_pass=None,
            match_score=None,
            fail_code="LOCAL_DETECT_FAIL",
        )

    display = similarity_to_display_score(sim)
    min_sim = config.FACE_LOCAL_MIN_SIMILARITY
    if sim < min_sim:
        return FaceVerifyOutcome(
            ok=False,
            reason=f"人脸验证失败：起止照片非同一人（相似度 {display}）",
            face_verified=False,
            liveness_pass=None,
            match_score=display,
            fail_code="NOT_SAME_PERSON",
        )

    return FaceVerifyOutcome(
        ok=True,
        reason="",
        face_verified=True,
        liveness_pass=None,
        match_score=display,
        fail_code=None,
    )


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


def verify_run_faces(evidence: list) -> FaceVerifyOutcome:
    """
    对跑步活动证据做人脸核验。
    返回 FaceVerifyOutcome；fail_code: MISSING_PHOTO | LIVENESS_FAIL | NOT_SAME_PERSON | PROVIDER_ERROR
    """
    start_url, end_url = _extract_face_urls(evidence)

    if not start_url and not end_url:
        return FaceVerifyOutcome(
            ok=False,
            reason="人脸验证失败：缺少起跑与结束照片",
            face_verified=False,
            liveness_pass=False,
            match_score=None,
            fail_code="MISSING_PHOTO",
        )
    if not start_url:
        return FaceVerifyOutcome(
            ok=False,
            reason="人脸验证失败：缺少起跑照片",
            face_verified=False,
            liveness_pass=False,
            match_score=None,
            fail_code="MISSING_PHOTO",
        )
    if not end_url:
        return FaceVerifyOutcome(
            ok=False,
            reason="人脸验证失败：缺少结束照片",
            face_verified=False,
            liveness_pass=False,
            match_score=None,
            fail_code="MISSING_PHOTO",
        )

    provider = (config.FACE_PROVIDER or "none").lower()
    if provider == "none":
        return FaceVerifyOutcome(
            ok=True,
            reason="",
            face_verified=True,
            liveness_pass=None,
            match_score=None,
            fail_code=None,
        )

    if provider == "local":
        return _verify_run_faces_local(start_url, end_url)

    if provider != "tencent":
        return FaceVerifyOutcome(
            ok=True,
            reason="",
            face_verified=True,
            liveness_pass=None,
            match_score=None,
            fail_code=None,
        )

    start_b64 = _read_image_b64(start_url)
    end_b64 = _read_image_b64(end_url)
    if not start_b64 or not end_b64:
        return FaceVerifyOutcome(
            ok=True,
            reason="",
            face_verified=True,
            liveness_pass=None,
            match_score=None,
            fail_code="PROVIDER_SKIP_LOCAL",
        )

    live_start, err_s = _tencent_liveness(start_b64)
    if not live_start:
        msg = "人脸验证失败：起跑照片未通过活体检测"
        if err_s:
            msg += f"（{err_s}）"
        return FaceVerifyOutcome(
            ok=False,
            reason=msg,
            face_verified=False,
            liveness_pass=False,
            match_score=None,
            fail_code="LIVENESS_FAIL",
        )

    live_end, err_e = _tencent_liveness(end_b64)
    if not live_end:
        msg = "人脸验证失败：结束照片未通过活体检测"
        if err_e:
            msg += f"（{err_e}）"
        return FaceVerifyOutcome(
            ok=False,
            reason=msg,
            face_verified=False,
            liveness_pass=False,
            match_score=None,
            fail_code="LIVENESS_FAIL",
        )

    score, err_c = _tencent_compare(start_b64, end_b64)
    if score is None:
        return FaceVerifyOutcome(
            ok=True,
            reason="",
            face_verified=True,
            liveness_pass=True,
            match_score=None,
            fail_code="COMPARE_UNAVAILABLE",
        )

    if score < config.FACE_MATCH_THRESHOLD:
        return FaceVerifyOutcome(
            ok=False,
            reason=f"人脸验证失败：起止照片非同一人（相似度 {score:.1f}）",
            face_verified=False,
            liveness_pass=True,
            match_score=score,
            fail_code="NOT_SAME_PERSON",
        )

    return FaceVerifyOutcome(
        ok=True,
        reason="",
        face_verified=True,
        liveness_pass=True,
        match_score=score,
        fail_code=None,
    )


def apply_face_outcome_to_activity(activity, outcome: FaceVerifyOutcome) -> None:
    activity.face_verified = outcome.face_verified
    activity.face_liveness_pass = outcome.liveness_pass
    activity.face_match_score = outcome.match_score
    activity.face_fail_code = outcome.fail_code
