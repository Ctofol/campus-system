"""
Local InsightFace helpers for self-hosted face verification.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

import numpy as np

from .. import config

logger = logging.getLogger(__name__)

MODEL_VERSION = f"insightface:{config.FACE_INSIGHTFACE_MODEL or 'buffalo_l'}"

_face_app = None
_init_error: Optional[str] = None


@dataclass
class FaceEmbeddingResult:
    embedding: Optional[np.ndarray]
    error: str = ""
    quality: Optional[Dict[str, Any]] = None


def _get_face_app():
    global _face_app, _init_error
    if _face_app is not None:
        return _face_app, None
    if _init_error:
        return None, _init_error
    try:
        from insightface.app import FaceAnalysis
    except ImportError as e:
        _init_error = f"missing dependency: {e}; please install insightface and onnxruntime"
        return None, _init_error

    try:
        providers = [
            p.strip()
            for p in (config.FACE_INSIGHTFACE_PROVIDERS or "CPUExecutionProvider").split(",")
            if p.strip()
        ]
        app = FaceAnalysis(name=config.FACE_INSIGHTFACE_MODEL or "buffalo_l", providers=providers)
        app.prepare(ctx_id=0, det_size=(640, 640))
        _face_app = app
        return _face_app, None
    except Exception as e:
        _init_error = str(e)
        logger.exception("InsightFace init failed")
        return None, _init_error


def _read_image_bgr(path: str):
    import cv2

    img = cv2.imread(path)
    if img is None:
        return None
    return img


def _face_area(face) -> float:
    bbox = getattr(face, "bbox", None)
    if bbox is None:
        return 0.0
    return float(max(0.0, bbox[2] - bbox[0]) * max(0.0, bbox[3] - bbox[1]))


def _largest_face(faces):
    if not faces:
        return None
    return max(faces, key=_face_area)


def _image_quality(img, face) -> Dict[str, Any]:
    import cv2

    h, w = img.shape[:2]
    area = max(1.0, float(w * h))
    bbox = getattr(face, "bbox", [0, 0, 0, 0])
    x1, y1, x2, y2 = [int(max(0, v)) for v in bbox]
    x2 = min(w, x2)
    y2 = min(h, y2)
    crop = img[y1:y2, x1:x2] if x2 > x1 and y2 > y1 else img
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    brightness = float(gray.mean()) if gray.size else 0.0
    sharpness = float(cv2.Laplacian(gray, cv2.CV_64F).var()) if gray.size else 0.0
    face_ratio = _face_area(face) / area
    quality_score = min(100.0, face_ratio * 900.0 + brightness * 0.25 + sharpness * 0.08)
    return {
        "face_count": 1,
        "face_ratio": round(face_ratio, 4),
        "brightness": round(brightness, 2),
        "sharpness": round(sharpness, 2),
        "quality_score": round(quality_score, 2),
    }


def _embedding_from_face(face) -> Optional[np.ndarray]:
    emb = getattr(face, "embedding", None)
    if emb is None:
        return None
    return np.asarray(emb, dtype=np.float32)


def extract_embedding(image_path: str) -> Tuple[Optional[np.ndarray], str]:
    app, err = _get_face_app()
    if app is None:
        return None, err or "InsightFace not initialized"
    img = _read_image_bgr(image_path)
    if img is None:
        return None, "cannot read image"
    face = _largest_face(app.get(img))
    if face is None:
        return None, "no face detected"
    emb = _embedding_from_face(face)
    if emb is None:
        return None, "face embedding unavailable"
    return emb, ""


def extract_verified_embedding(image_path: str) -> FaceEmbeddingResult:
    app, err = _get_face_app()
    if app is None:
        return FaceEmbeddingResult(None, err or "InsightFace not initialized")

    img = _read_image_bgr(image_path)
    if img is None:
        return FaceEmbeddingResult(None, "cannot read image")

    faces = app.get(img)
    if not faces:
        return FaceEmbeddingResult(None, "no face detected", {"face_count": 0})
    if len(faces) != 1:
        return FaceEmbeddingResult(None, "multiple faces detected", {"face_count": len(faces)})

    face = faces[0]
    quality = _image_quality(img, face)
    if quality["face_ratio"] < config.FACE_LOCAL_MIN_FACE_RATIO:
        return FaceEmbeddingResult(None, "face too small", quality)
    if quality["brightness"] < config.FACE_LOCAL_MIN_BRIGHTNESS:
        return FaceEmbeddingResult(None, "image too dark", quality)
    if quality["sharpness"] < config.FACE_LOCAL_MIN_SHARPNESS:
        return FaceEmbeddingResult(None, "image too blurry", quality)

    emb = _embedding_from_face(face)
    if emb is None:
        return FaceEmbeddingResult(None, "face embedding unavailable", quality)
    return FaceEmbeddingResult(emb, "", quality)


def extract_verified_embedding_from_bgr(img) -> FaceEmbeddingResult:
    app, err = _get_face_app()
    if app is None:
        return FaceEmbeddingResult(None, err or "InsightFace not initialized")
    if img is None:
        return FaceEmbeddingResult(None, "empty frame")

    faces = app.get(img)
    if not faces:
        return FaceEmbeddingResult(None, "no face detected", {"face_count": 0})
    if len(faces) != 1:
        return FaceEmbeddingResult(None, "multiple faces detected", {"face_count": len(faces)})

    face = faces[0]
    quality = _image_quality(img, face)
    if quality["face_ratio"] < config.FACE_LOCAL_MIN_FACE_RATIO:
        return FaceEmbeddingResult(None, "face too small", quality)
    if quality["brightness"] < config.FACE_LOCAL_MIN_BRIGHTNESS:
        return FaceEmbeddingResult(None, "image too dark", quality)
    if quality["sharpness"] < config.FACE_LOCAL_MIN_SHARPNESS:
        return FaceEmbeddingResult(None, "image too blurry", quality)

    emb = _embedding_from_face(face)
    if emb is None:
        return FaceEmbeddingResult(None, "face embedding unavailable", quality)
    return FaceEmbeddingResult(emb, "", quality)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    a = a.flatten()
    b = b.flatten()
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom < 1e-8:
        return 0.0
    return float(np.dot(a, b) / denom)


def compare_embeddings(a: np.ndarray, b: np.ndarray) -> float:
    return cosine_similarity(a, b)


def compare_two_images(path_a: str, path_b: str) -> Tuple[Optional[float], str]:
    res_a = extract_verified_embedding(path_a)
    if res_a.embedding is None:
        return None, f"start image: {res_a.error}"
    res_b = extract_verified_embedding(path_b)
    if res_b.embedding is None:
        return None, f"end image: {res_b.error}"
    return cosine_similarity(res_a.embedding, res_b.embedding), ""


def similarity_to_display_score(sim: float) -> float:
    return round(max(0.0, min(100.0, sim * 100.0)), 1)
