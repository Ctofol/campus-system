import sys
import os

sys.path.append(os.getcwd())

routers = ["teacher", "courses", "approvals", "student", "upload", "run_groups", "admin", "common", "auth", "user", "activity"]

for r in routers:
    try:
        exec(f"from app.routers import {r}")
        print(f"Router {r} OK")
    except Exception as e:
        print(f"Router {r} FAIL: {e}")
        import traceback
        traceback.print_exc()
