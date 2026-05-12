# -*- coding: utf-8 -*-
"""
冒烟测试（无需打开小程序）：教师登录 → 任务列表 → 任务详情 → 若有提交则 GET 任务运动详情。

前置：
  - 本地已启动后端：cd backend && uvicorn app.main:app --reload --port 8000
  - pip install requests
  - 库里有该教师的任务；若要学员提交记录可先跑 scripts/seed_mock_data.py（按需）

环境变量（可选）：
  API_BASE=http://127.0.0.1:8000
  TEACHER_PHONE=13800010001
  TEACHER_PASSWORD=123456
"""
from __future__ import annotations

import json
import os
import sys

try:
    import requests
except ImportError:
    print("请先安装依赖: pip install requests")
    sys.exit(1)

BASE = os.environ.get("API_BASE", "http://127.0.0.1:8000").rstrip("/")
PHONE = os.environ.get("TEACHER_PHONE", "13800010001")
PASSWORD = os.environ.get("TEACHER_PASSWORD", "123456")


def main() -> None:
    print(f"API_BASE={BASE} TEACHER_PHONE={PHONE}\n")

    try:
        r = requests.post(
            f"{BASE}/auth/login",
            json={"phone": PHONE, "password": PASSWORD},
            timeout=15,
        )
    except requests.exceptions.RequestException as e:
        print("无法连接后端。请先启动: cd backend && uvicorn app.main:app --reload --port 8000")
        print(f"原因: {e}")
        sys.exit(1)
    if r.status_code != 200:
        print("登录失败:", r.status_code, r.text[:600])
        sys.exit(1)

    body = r.json()
    token = body.get("access_token")
    role = body.get("role")
    print(f"登录 OK  role={role}")

    headers = {"Authorization": f"Bearer {token}"}

    r = requests.get(f"{BASE}/teacher/tasks?page=1&size=20&status=active", headers=headers, timeout=15)
    print(f"\nGET /teacher/tasks -> HTTP {r.status_code}")
    if r.status_code != 200:
        print(r.text[:800])
        sys.exit(1)

    data = r.json()
    items = data.get("items") or []
    if not items:
        print(
            "暂无任务。可在小程序教师端发布任务，或执行: python scripts/seed_mock_data.py"
        )
        sys.exit(0)

    first = items[0]
    tid = first["id"]
    print(f"选用任务 id={tid} title={first.get('title')!r}")

    r = requests.get(f"{BASE}/teacher/tasks/{tid}", headers=headers, timeout=15)
    print(f"\nGET /teacher/tasks/{tid} -> HTTP {r.status_code}")
    if r.status_code != 200:
        print(r.text[:800])
        sys.exit(1)

    detail = r.json()
    ss = detail.get("student_statuses") or []
    print(
        f"  total_students={detail.get('total_students')} "
        f"completed_count={detail.get('completed_count')} "
        f"学员行数={len(ss)}"
    )

    activity_id = None
    for row in ss[:8]:
        sid = row.get("student_id")
        name = row.get("student_name")
        st = row.get("status")
        aid = row.get("activity_id")
        mv = row.get("metric_value")
        print(f"    student_id={sid} name={name!r} status={st} activity_id={aid} metric={mv!r}")
        if aid and activity_id is None:
            activity_id = aid

    if not activity_id:
        print("\n暂无学员任务提交（activity_id 为空），跳过 GET /teacher/task-runs/{id}")
        print("完成一条学生任务跑提交后再运行本脚本即可验证详情接口。")
        return

    r = requests.get(f"{BASE}/teacher/task-runs/{activity_id}", headers=headers, timeout=15)
    print(f"\nGET /teacher/task-runs/{activity_id} -> HTTP {r.status_code}")
    if r.status_code != 200:
        print(r.text[:800])
        sys.exit(1)

    tr = r.json()
    metrics = tr.get("metrics") or {}
    act = tr.get("activity") or {}
    print(
        "  task_run_detail:",
        json.dumps(
            {
                "activity_id": act.get("id"),
                "task_title": act.get("task_title"),
                "distance_km": metrics.get("distance"),
                "duration_sec": metrics.get("duration"),
                "has_trajectory": bool(metrics.get("trajectory")),
            },
            ensure_ascii=False,
        ),
    )
    print("\n冒烟通过：教师端查看任务数据链路可用（当前环境下）。")


if __name__ == "__main__":
    main()
