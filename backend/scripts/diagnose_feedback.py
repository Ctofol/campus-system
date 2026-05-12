#!/usr/bin/env python3
"""命令行调用反馈诊断（与 FastAPI 共用逻辑）。用法: echo 反馈内容 | python diagnose_feedback.py"""
import json
import os
import sys

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from app.services.feedback_diagnosis import diagnose_feedback  # noqa: E402


def main() -> None:
    text = sys.stdin.read().strip() or " ".join(sys.argv[1:])
    result = diagnose_feedback(text, prefer_llm=True)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
