"""
Warm up InsightFace before starting the backend.

This script forces model initialization so the first real face request
does not spend time downloading the model.

Usage:
  cd backend
  python scripts/warmup_insightface.py
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main() -> int:
    try:
        from insightface.app import FaceAnalysis
    except ImportError as exc:
        print(f"[warmup] missing dependency: {exc}")
        return 2

    from app import config

    providers = [
        p.strip()
        for p in (config.FACE_INSIGHTFACE_PROVIDERS or "CPUExecutionProvider").split(",")
        if p.strip()
    ]
    model_name = config.FACE_INSIGHTFACE_MODEL or "buffalo_l"

    print(f"[warmup] initializing InsightFace model: {model_name}")
    print(f"[warmup] providers: {', '.join(providers) if providers else 'CPUExecutionProvider'}")
    try:
        app = FaceAnalysis(name=model_name, providers=providers)
        app.prepare(ctx_id=0, det_size=(640, 640))
    except Exception as exc:
        print(f"[warmup] failed: {exc}")
        return 3

    model_root = os.path.expanduser("~/.insightface/models")
    print(f"[warmup] ready, cache directory: {model_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
