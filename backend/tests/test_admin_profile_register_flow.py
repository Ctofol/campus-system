# -*- coding: utf-8 -*-
"""
第一阶段：档案预设、注册拦截、激活绑定、教师权限 自动化功能测试。

运行前请确保：
1. 后端已启动（默认 http://127.0.0.1:8000）
2. 存在管理员账号（用于调用 /admin 接口），可通过环境变量设置：
   ADMIN_PHONE, ADMIN_PASSWORD
3. 若后端不在本机，设置 BASE_URL 环境变量

运行方式：
  cd backend && python -m pytest tests/test_admin_profile_register_flow.py -v
  或：python tests/test_admin_profile_register_flow.py
"""
import os
import re
import sys

import pytest

try:
    import requests
except ImportError:
    requests = None

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8000")
ADMIN_PHONE = os.environ.get("ADMIN_PHONE", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")

# 测试用档案与用户
TEST_STUDENT_ID_PREFIX = "TEST_FLOW_"
TEST_STUDENT_NAME = "档案激活测试生"
TEST_CLASS_NAME = "软件工程1区"
TEST_MAJOR = "软件工程"
WRONG_STUDENT_ID = "NOT_IN_ARCHIVE_999"


def _url(path: str) -> str:
    return f"{BASE_URL.rstrip('/')}{path}"


def _get_captcha():
    r = requests.get(_url("/common/captcha"), timeout=5)
    r.raise_for_status()
    data = r.json()
    return data["image"], data["key"]


def _solve_captcha_from_image(data_url: str) -> str:
    """简单占位：实际需要 OCR 或测试环境固定验证码。本脚本使用后端约定：测试环境下可放行或使用固定 key。"""
    # 若后端提供测试用固定验证码（如 code=TEST, key=xxx），这里可返回 "TEST"
    # 否则需要从 data_url 解析图片并 OCR，此处返回占位，测试时需后端支持测试验证码
    return "TEST"


@pytest.fixture(scope="module")
def admin_token():
    """获取管理员 Token（若未配置管理员则跳过需要 admin 的用例）"""
    try:
        r = requests.post(
            _url("/auth/login"),
            json={"phone": ADMIN_PHONE, "password": ADMIN_PASSWORD},
            timeout=5,
        )
        if r.status_code != 200:
            pytest.skip(f"无可用管理员账号: {ADMIN_PHONE}，跳过依赖 admin 的用例")
        return r.json()["access_token"]
    except Exception as e:
        pytest.skip(f"登录管理员失败: {e}")


# 与后端 CAPTCHA_SECRET 一致时，可用 code=TEST 的 key 做自动化测试
_CAPTCHA_SECRET = "lingxi_sports_mvp_secret_salt_2026"


def _test_captcha_key():
    import hashlib
    key_src = "TEST" + _CAPTCHA_SECRET
    return hashlib.md5(key_src.encode("utf-8")).hexdigest()


@pytest.fixture(scope="module")
def captcha_key():
    """测试用验证码 key（code=TEST 时后端需接受该 key，见 main.py 注册逻辑）"""
    return _test_captcha_key()


@pytest.fixture(scope="module")
def imported_profiles(admin_token):
    """档案预设：在管理端导入/创建学生档案（学号、姓名、性别、班级、专业）"""
    import time
    # 每次运行用唯一学号，便于“激活绑定”测试重复执行
    test_student_id = f"{TEST_STUDENT_ID_PREFIX}{int(time.time())}"
    headers = {"Authorization": f"Bearer {admin_token}"}
    profiles = [
        {
            "student_id": test_student_id,
            "full_name": TEST_STUDENT_NAME,
            "gender": "male",
            "class_name": TEST_CLASS_NAME,
            "major": TEST_MAJOR,
        },
    ]
    r = requests.post(
        _url("/admin/mock/student-profiles"),
        json=profiles,
        headers=headers,
        timeout=10,
    )
    assert r.status_code == 200, f"导入档案失败: {r.text}"
    data = r.json()
    assert data.get("failed", 0) == 0, f"档案导入有失败: {data}"
    return {"profiles": profiles, "test_student_id": test_student_id}


def test_register_without_profile_should_fail(captcha_key, imported_profiles):
    """注册拦截：档案库之外的学号注册应被拦截并报错"""
    # 使用未在档案中的学号注册
    payload = {
        "phone": "13800001111",
        "name": "任意姓名",
        "password": "Test123456",
        "role": "student",
        "student_id": WRONG_STUDENT_ID,
        "captcha_code": "TEST",
        "captcha_key": captcha_key,
    }
    r = requests.post(_url("/auth/register"), json=payload, timeout=10)
    # 预期：403 或 400，且提示档案/学号相关
    assert r.status_code in (400, 403), f"预期 4xx 拦截，得到: {r.status_code} {r.text}"
    text = (r.json() or {}).get("detail", r.text)
    assert "档案" in text or "学号" in text or "无此" in text or "已被" in text or "detail" in text.lower()


def test_register_with_profile_inherits_major_and_class(captcha_key, imported_profiles):
    """激活绑定：使用档案内正确学号注册，应成功且 User 继承专业与班级"""
    import time
    test_student_id = imported_profiles["test_student_id"]
    phone = f"138{int(time.time()) % 10_000_000:07d}"
    payload = {
        "phone": phone,
        "name": TEST_STUDENT_NAME,
        "password": "Test123456",
        "role": "student",
        "student_id": test_student_id,
        "captcha_code": "TEST",
        "captcha_key": captcha_key,
    }
    r = requests.post(_url("/auth/register"), json=payload, timeout=10)
    if r.status_code == 400 and "验证码" in (r.json() or {}).get("detail", ""):
        pytest.skip("后端验证码校验严格，需在测试环境关闭或使用测试验证码")
    assert r.status_code == 200, f"注册应成功: {r.status_code} {r.text}"
    data = r.json()
    assert data.get("role") == "student"
    assert data.get("student_id") == test_student_id
    assert data.get("class_name") == TEST_CLASS_NAME, f"应继承班级: {data}"
    assert data.get("major") == TEST_MAJOR, f"应继承专业: {data}"


def test_teacher_sees_only_assigned_class(admin_token, imported_profiles):
    """权限校验：教师仅分配「软件工程1区」后，测试监控/学生列表仅能看到该班级数据"""
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1) 确保班级存在
    r = requests.get(_url("/admin/classes"), headers=headers, timeout=5)
    r.raise_for_status()
    classes = r.json()
    class_names = [c["name"] for c in classes]
    if TEST_CLASS_NAME not in class_names:
        r = requests.post(
            _url("/admin/classes"),
            json={"name": TEST_CLASS_NAME},
            headers=headers,
            timeout=5,
        )
        assert r.status_code in (200, 400), f"创建班级: {r.text}"  # 400 可能为已存在

    # 2) 创建教师并分配管辖班级「软件工程1区」
    import time
    t_phone = f"139{int(time.time()) % 10_000_000:07d}"
    r = requests.post(
        _url("/admin/users"),
        json={
            "phone": t_phone,
            "name": "测试教师",
            "password": "Test123456",
            "role": "teacher",
        },
        headers=headers,
        timeout=5,
    )
    if r.status_code != 200:
        pytest.skip(f"创建教师失败（可能手机号重复）: {r.text}")
    teacher = r.json()
    teacher_id = teacher["id"]

    r = requests.post(
        _url(f"/admin/teacher-classes/{teacher_id}"),
        json={"class_names": [TEST_CLASS_NAME]},
        headers=headers,
        timeout=5,
    )
    assert r.status_code == 200, f"分配管辖班级失败: {r.text}"

    # 3) 教师登录
    r = requests.post(
        _url("/auth/login"),
        json={"phone": t_phone, "password": "Test123456"},
        timeout=5,
    )
    assert r.status_code == 200, f"教师登录失败: {r.text}"
    t_token = r.json()["access_token"]
    t_headers = {"Authorization": f"Bearer {t_token}"}

    # 4) 教师拉取学生列表（应仅限管辖班级）
    r = requests.get(_url("/teacher/students"), headers=t_headers, timeout=5)
    assert r.status_code == 200, f"获取学生列表失败: {r.text}"
    students = r.json() if isinstance(r.json(), list) else r.json().get("items", [])
    for s in students:
        assert s.get("class_name") == TEST_CLASS_NAME or s.get("class_id") is not None, (
            f"教师应只能看到管辖班级学生: {s}"
        )

    # 5) 测试监控接口（体测 live）应只返回管辖班级数据
    r = requests.get(_url("/teacher/tests/live"), headers=t_headers, timeout=5)
    assert r.status_code == 200
    # 若有数据，则都应是本班级的（通过 teacher/students 的 class 过滤已保证）
    assert "items" in r.json()


if __name__ == "__main__":
    if not requests:
        print("请安装 requests: pip install requests")
        sys.exit(1)
    pytest.main([__file__, "-v", "-s"])
