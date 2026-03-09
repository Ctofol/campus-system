#!/usr/bin/env python3
"""
创建测试教师用户
"""
import sys
sys.path.insert(0, '.')

from app import models, database, auth

def create_teacher_user():
    """创建测试教师用户"""
    db = database.SessionLocal()
    
    try:
        # 检查教师用户是否已存在
        existing_teacher = db.query(models.User).filter(
            models.User.phone == '13900139000'
        ).first()
        
        if existing_teacher:
            print("测试教师已存在！")
            print(f"姓名: {existing_teacher.name}")
            print(f"手机号: {existing_teacher.phone}")
            print(f"角色: {existing_teacher.role}")
            print("\n请使用以下凭据登录:")
            print("手机号: 13900139000")
            print("密码: 123456")
            return
        
        # 创建新教师用户
        teacher = models.User(
            name='测试教师',
            phone='13900139000',
            password_hash=auth.get_password_hash('123456'),
            role='teacher',
            student_id='T2024001'  # 教师工号
        )
        db.add(teacher)
        db.commit()
        db.refresh(teacher)
        
        print("✅ 测试教师创建成功！")
        print("\n登录凭据:")
        print("=" * 40)
        print(f"手机号: 13900139000")
        print(f"密码: 123456")
        print(f"姓名: {teacher.name}")
        print(f"角色: {teacher.role}")
        print("=" * 40)
        print("\n请在登录页面使用上述手机号和密码登录")
        
    except Exception as e:
        print(f"❌ 创建教师失败: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("正在创建测试教师...")
    create_teacher_user()