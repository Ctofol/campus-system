#!/usr/bin/env python3
"""
创建测试数据
"""
import sys
sys.path.insert(0, '.')

from app import models, database
from datetime import datetime, timedelta
import json

def create_test_data():
    """创建测试数据"""
    db = database.SessionLocal()
    
    try:
        # 获取学生和教师用户
        student = db.query(models.User).filter(models.User.role == 'student').first()
        teacher = db.query(models.User).filter(models.User.role == 'teacher').first()
        
        if not student:
            print("❌ 未找到学生用户，请先创建学生用户")
            return
            
        if not teacher:
            print("❌ 未找到教师用户，请先创建教师用户")
            return
        
        print(f"找到学生: {student.name} (ID: {student.id})")
        print(f"找到教师: {teacher.name} (ID: {teacher.id})")
        
        # 1. 创建健康申请
        health_request = models.HealthRequest(
            student_id=student.id,
            type="leave",
            reason="感冒发烧，需要请假休息",
            status="pending",
            attachments=json.dumps([
                "uploads/202603/ae12b1bf-3b9f-4a98-927d-64e7f4b8e5af.jpg"
            ])
        )
        db.add(health_request)
        
        # 2. 创建跑步任务
        run_task = models.Task(
            title="晨跑训练",
            type="run",
            description="每日晨跑5公里，提高体能",
            min_distance=5.0,
            min_duration=30,
            created_by=teacher.id,
            video_url="uploads/1256f1dd-d1ad-4cbd-b3e5-c4919e53b8dd.webm"
        )
        db.add(run_task)
        
        # 3. 创建体测任务
        fitness_task = models.Task(
            title="体能测试",
            type="test",
            description="包含50米跑、立定跳远、仰卧起坐等项目",
            created_by=teacher.id,
            video_url="uploads/57c61e1f-5307-436e-a39b-89a1f28e1ef0.webm"
        )
        db.add(fitness_task)
        
        db.commit()
        
        # 获取创建的任务ID
        db.refresh(run_task)
        db.refresh(fitness_task)
        
        # 4. 创建活动记录（模拟学生完成任务）
        from datetime import datetime, timedelta
        
        # 跑步活动
        run_activity = models.Activity(
            user_id=student.id,
            type="run",
            source="task",
            status="approved",
            started_at=datetime.now() - timedelta(hours=1),
            ended_at=datetime.now() - timedelta(minutes=30)
        )
        db.add(run_activity)
        db.commit()
        db.refresh(run_activity)
        
        # 跑步活动指标
        run_metrics = models.ActivityMetrics(
            activity_id=run_activity.id,
            distance=5.2,
            duration=1530,  # 25分30秒
            pace="4:54",
            qualified=True,
            teacher_score=85.0,
            teacher_comment="跑步姿势标准，速度有待提高",
            scored_at=datetime.now(),
            scored_by=teacher.id
        )
        db.add(run_metrics)
        
        # 体测活动
        fitness_activity = models.Activity(
            user_id=student.id,
            type="test",
            source="task",
            status="approved",
            started_at=datetime.now() - timedelta(hours=2),
            ended_at=datetime.now() - timedelta(hours=1, minutes=30)
        )
        db.add(fitness_activity)
        db.commit()
        db.refresh(fitness_activity)
        
        # 体测活动指标
        fitness_metrics = models.ActivityMetrics(
            activity_id=fitness_activity.id,
            count=45,
            duration=3600,  # 1小时
            qualified=True,
            teacher_score=92.0,
            teacher_comment="各项指标优秀，继续保持",
            scored_at=datetime.now(),
            scored_by=teacher.id
        )
        db.add(fitness_metrics)
        
        # 5. 更新学生的常规成绩
        student.regular_score = (85.0 + 92.0) / 2  # 平均分
        
        db.commit()
        
        print("\n✅ 测试数据创建成功！")
        print("\n创建的数据:")
        print("=" * 50)
        print(f"📋 健康申请: 1条 (状态: 待审核)")
        print(f"🏃 跑步任务: {run_task.title}")
        print(f"💪 体测任务: {fitness_task.title}")
        print(f"✅ 活动记录: 2条 (跑步+体测)")
        print(f"📊 学生常规成绩: {student.regular_score}分")
        print("=" * 50)
        print("\n现在可以登录查看数据了！")
        
    except Exception as e:
        print(f"❌ 创建测试数据失败: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("正在创建测试数据...")
    create_test_data()