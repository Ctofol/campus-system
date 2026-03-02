#!/usr/bin/env python3
"""
快速创建测试用户
"""
import sys
sys.path.insert(0, '.')

from app import models, database, auth

def create_test_user():
    """创建测试用户"""
    db = database.SessionLocal()
    
    try:
        # 检查用户是否已存在
        existing_user = db.query(models.User).filter(
            models.User.phone == '13800138000'
        ).first()
        
        if existing_user:
            print("测试用户已存在！")
            print(f"姓名: {existing_user.name}")
            print(f"手机号: {existing_user.phone}")
            print(f"角色: {existing_user.role}")
            print("\n请使用以下凭据登录:")
            print("手机号: 13800138000")
            print("密码: 123456")
            return
        
        # 创建新用户
        user = models.User(
            name='测试学生',
            phone='13800138000',
            password_hash=auth.get_password_hash('123456'),
            role='student',
            student_id='2024001'
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print("✅ 测试用户创建成功！")
        print("\n登录凭据:")
        print("=" * 40)
        print(f"手机号: 13800138000")
        print(f"密码: 123456")
        print(f"姓名: {user.name}")
        print(f"角色: {user.role}")
        print("=" * 40)
        print("\n请在登录页面使用上述手机号和密码登录")
        
    except Exception as e:
        print(f"❌ 创建用户失败: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("正在创建测试用户...")
    create_test_user()