"""
本地人脸 1:1 比对（InsightFace），不调用腾讯云。
"""
from __future__ import annotations

import logging
from functools import lru_cache
from typing import List, Optional, Tuple

import numpy as np

from .. import config

logger = logging.getLogger(__name__)

_face_app = None
_init_error: Optional[str] = None


def _get_face_app():
    global _face_app, _init_error
    if _face_app is not None:
        return _face_app, None
    if _init_error:
        return None, _init_error
    try:
        import cv2  # noqa: F401
        from insightface.app import FaceAnalysis
    except ImportError as e:
        _init_error = f"缺少依赖: {e}（请 pip install insightface onnxruntime）"
        return None, _init_error

    try:
        name = config.FACE_INSIGHTFACE_MODEL or "buffalo_l"
        providers = config.FACE_INSIGHTFACE_PROVIDERS.split(",")
        app = FaceAnalysis(name=name, providers=[p.strip() for p in providers if p.strip()])
        app.prepare(ctx_id=0, det_size=(640, 640))
        _face_app = app
        return _face_app, None
    except Exception as e:
        _init_error = str(e)
        logger.exception("InsightFace init failed")
        return None, _init_error


def _largest_face_embedding(faces) -> Optional[np.ndarray]:
    if not faces:
        return None
    best = max(faces, key=lambda f: float((f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1])))
    emb = getattr(best, "embedding", None)
    if emb is None:
        return None
    return np.asarray(emb, dtype=np.float32)


def _read_image_bgr(path: str):
    import cv2

    img = cv2.imread(path)
    if img is None:
        return None
    return img


def extract_embedding(image_path: str) -> Tuple[Optional[np.ndarray], str]:
    app, err = _get_face_app()
    if app is None:
        return None, err or "InsightFace 未初始化"
    img = _read_image_bgr(image_path)
    if img is None:
        return None, "无法读取图片"
    faces = app.get(img)
    emb = _largest_face_embedding(faces)
    if emb is None:
        return None, "未检测到人脸"
    return emb, ""


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    a = a.flatten()
    b = b.flatten()
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom < 1e-8:
        return 0.0
    return float(np.dot(a, b) / denom)


def compare_two_images(path_a: str, path_b: str) -> Tuple[Optional[float], str]:
    """
    返回 (相似度 0~1, 错误信息)。相似度越高越像同一人。
    """
    emb_a, err_a = extract_embedding(path_a)
    if emb_a is None:
        return None, f"起跑照: {err_a}"
    emb_b, err_b = extract_embedding(path_b)
    if emb_b is None:
        return None, f"结束照: {err_b}"
    sim = cosine_similarity(emb_a, emb_b)
    return sim, ""


def similarity_to_display_score(sim: float) -> float:
    """映射为 0–100，便于与 FACE_MATCH_THRESHOLD 对齐。"""
    return round(max(0.0, min(100.0, sim * 100.0)), 1)
