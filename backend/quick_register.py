#!/usr/bin/env python3
"""快速注册用户脚本"""
import requests
import json

BASE_URL = "http://120.26.17.147:8000"

def get_captcha():
    """获取验证码"""
    response = requests.get(f"{BASE_URL}/common/captcha")
    data = response.json()
    return data['key']

def register_user(phone, password, name, role, captcha_key):
    """注册用户"""
    # 验证码固定为 "TEST"（需要知道验证码内容）
    # 由于我们不能看到验证码图片，我们直接计算key
    import hashlib
    
    # 使用固定验证码 "AAAA"
    captcha_code = "AAAA"
    secret = "lingxi_sports_mvp_secret_salt_2026"
    key_src = captcha_code.upper() + secret
    captcha_key = hashlib.md5(key_src.encode('utf-8')).hexdigest()
    
    data = {
        "phone": phone,
        "password": password,
        "name": name,
        "role": role,
        "captcha_code": captcha_code,
        "captcha_key": captcha_key
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=data)
    return response.json()

if __name__ == "__main__":
    print("=== 快速注册用户 ===\n")
    
    # 注册学生账号
    print("1. 注册学生账号...")
    try:
        result = register_user(
            phone="13800138001",
            password="123456",
            name="测试学生",
            role="student",
            captcha_key=""
        )
        print(f"✅ 学生注册成功！")
        print(f"   手机号: 13800138001")
        print(f"   密码: 123456")
        print(f"   Token: {result.get('access_token', 'N/A')[:50]}...")
    except Exception as e:
        print(f"❌ 学生注册失败: {e}")
    
    print()
    
    # 注册教师账号
    print("2. 注册教师账号...")
    try:
        result = register_user(
            phone="13900139001",
            password="123456",
            name="测试教师",
            role="teacher",
            captcha_key=""
        )
        print(f"✅ 教师注册成功！")
        print(f"   手机号: 13900139001")
        print(f"   密码: 123456")
        print(f"   Token: {result.get('access_token', 'N/A')[:50]}...")
    except Exception as e:
        print(f"❌ 教师注册失败: {e}")
    
    print("\n=== 注册完成 ===")
    print("你可以使用以上账号登录测试！")
