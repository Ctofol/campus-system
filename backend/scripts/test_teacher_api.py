# -*- coding: utf-8 -*-
"""Quick test: login as teacher, GET /teacher/stats and /teacher/students."""
import requests

BASE = "http://127.0.0.1:8000"

def main():
    # 教师A: 13800010001 管 信息安全1区+网络安全1区；教师B: 13800010002 管 数警2区
    r = requests.post(f"{BASE}/auth/login", json={"phone": "13800010001", "password": "123456"}, timeout=5)
    r.raise_for_status()
    token = r.json()["access_token"]
    print("Login OK, role:", r.json().get("role"))

    for name, url in [("stats", f"{BASE}/teacher/stats"), ("students", f"{BASE}/teacher/students?page=1&size=5")]:
        r2 = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=5)
        print(f"\n{name}: status={r2.status_code}")
        if r2.status_code != 200:
            print("body:", r2.text[:800])
        else:
            d = r2.json()
            if name == "stats":
                print("  student_count:", d.get("student_count"), "task_count:", d.get("task_count"),
                      "qualified_rate:", d.get("qualified_rate"), "completion_rate:", d.get("completion_rate"))
            else:
                print("  list length:", len(d) if isinstance(d, list) else "N/A", d if not isinstance(d, list) else "")

if __name__ == "__main__":
    main()
