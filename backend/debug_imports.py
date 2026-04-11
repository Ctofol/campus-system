import sys
import os

sys.path.append(os.getcwd())

try:
    from fastapi import Body
    print("FastAPI Body OK")
except Exception as e:
    print(f"FastAPI Body FAIL: {e}")

try:
    from app.routers import teacher
    print("Router teacher OK")
except Exception as e:
    print(f"Router teacher FAIL")
    import traceback
    traceback.print_exc()

try:
    from app.routers import auth
    print("Router auth OK")
except Exception as e:
    print(f"Router auth FAIL")
    import traceback
    traceback.print_exc()
