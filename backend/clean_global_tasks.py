"""
清理全局任务（class_id 为 NULL 的任务）
这些任务会显示给所有学生，包括新注册的学生
"""
from app.database import SessionLocal
from app.models import Task

def clean_global_tasks():
    db = SessionLocal()
    try:
        # 查询所有全局任务
        global_tasks = db.query(Task).filter(Task.class_id == None).all()
        
        print(f"找到 {len(global_tasks)} 个全局任务:")
        for task in global_tasks:
            print(f"  - Task {task.id}: {task.title} (创建者: {task.created_by})")
        
        if global_tasks:
            confirm = input("\n是否删除这些全局任务? (y/n): ")
            if confirm.lower() == 'y':
                for task in global_tasks:
                    db.delete(task)
                db.commit()
                print(f"✅ 已删除 {len(global_tasks)} 个全局任务")
            else:
                print("❌ 取消删除")
        else:
            print("✅ 没有找到全局任务")
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clean_global_tasks()
