import requests

BASE_URL = "http://localhost:8080"

def test_common():
    print("Testing /common/majors...")
    res = requests.get(f"{BASE_URL}/common/majors")
    print(res.json())
    
    if res.json():
        major_id = res.json()[0]['id']
        print(f"Testing /common/classes for major_id={major_id}...")
        res = requests.get(f"{BASE_URL}/common/classes?major_id={major_id}")
        print(res.json())

def test_login_teacher():
    print("Testing Teacher Login...")
    # Student1 (student_1) is 13900000001
    # Teacher1 is 13800000001
    res = requests.post(f"{BASE_URL}/auth/login", json={
        "phone": "13800000001",
        "password": "123456"
    })
    print(res.json())
    token = res.json().get('access_token')
    
    if token:
        print("Testing Teacher Dashboard Stats...")
        headers = {"Authorization": f"Bearer {token}"}
        res = requests.get(f"{BASE_URL}/teacher/dashboard/stats", headers=headers)
        print(res.json())

if __name__ == "__main__":
    try:
        test_common()
        test_login_teacher()
    except Exception as e:
        print(f"Error: {e}")
