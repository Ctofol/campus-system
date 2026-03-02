#!/usr/bin/env python3
"""
列出数据库中的所有用户
"""
import sys
sys.path.insert(0, '.')

from app import models, database

def list_users():
    """列出所有用户"""
    db = database.SessionLocal()
    
    try:
        users = db.query(models.User).all()
        
        if not users:
            print("数据库中没有用户")
            return
        
        print(f"\n数据库中共有 {len(users)} 个用户:\n")
        print("=" * 80)
        print(f"{'ID':<5} {'姓名':<15} {'手机号':<15} {'角色':<10} {'学号':<15}")
        print("=" * 80)
        
        for user in users:
            print(f"{user.id:<5} {user.name:<15} {user.phone:<15} {user.role:<10} {user.student_id or 'N/A':<15}")
        
        print("=" * 80)
        print(f"\n总计: {len(users)} 个用户")
        
    except Exception as e:
        print(f"❌ 查询失败: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    list_users()
