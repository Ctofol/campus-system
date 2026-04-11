import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_endpoint(name, method, path, data=None, headers=None):
    url = f"{BASE_URL}{path}"
    print(f"Testing {name} ({method} {path})...", end=" ", flush=True)
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=5)
        else:
            print("FAILED (Unsupported method)")
            return None

        if response.status_code < 300:
            print("OK")
            return response.json()
        else:
            print(f"FAILED (Status {response.status_code})")
            # print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"ERROR ({str(e)})")
        return None

def run_tests():
    print("=== Campus System API Test Suite ===\n")

    # 1. Root
    root = test_endpoint("Root", "GET", "/")
    if not root:
        print("Root endpoint failed. Is the server running?")
        return

    # 2. Student Login
    print("\n--- Student Tests ---")
    student_login_data = {
        "phone": "13800138000",
        "password": "123456"
    }
    s_login_res = test_endpoint("Student Login", "POST", "/auth/login", data=student_login_data)
    if s_login_res:
        s_token = s_login_res.get("access_token")
        s_headers = {"Authorization": f"Bearer {s_token}"}
        test_endpoint("Student Profile", "GET", "/users/profile", headers=s_headers)
        test_endpoint("Courses List", "GET", "/courses/", headers=s_headers)
        test_endpoint("Activity History", "GET", "/activity/history", headers=s_headers)
    else:
        print("Student login failed. Skipping student tests.")

    # 3. Teacher Login
    print("\n--- Teacher Tests ---")
    teacher_login_data = {
        "phone": "13900139000",
        "password": "123456"
    }
    t_login_res = test_endpoint("Teacher Login", "POST", "/auth/login", data=teacher_login_data)
    if t_login_res:
        t_token = t_login_res.get("access_token")
        t_headers = {"Authorization": f"Bearer {t_token}"}
        test_endpoint("Teacher Profile", "GET", "/users/profile", headers=t_headers)
        test_endpoint("Teacher Dashboard Stats", "GET", "/teacher/dashboard/stats", headers=t_headers)
        test_endpoint("Teacher Students List", "GET", "/teacher/students", headers=t_headers)
    else:
        print("Teacher login failed. Check if teacher user exists (run create_teacher.py).")

    print("\n=== Test Completed ===")

if __name__ == "__main__":
    run_tests()
