"""
Data seeding script for Campus Sports Health System
Generates realistic test data for development and testing
"""
import sys
import os
from datetime import datetime, timedelta
import random

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine
from app import models, auth

def seed_database():
    """Seed the database with test data"""
    db = SessionLocal()
    
    try:
        print("🌱 Starting database seeding...")
        
        # 1. Create Teacher
        print("\n📚 Creating teacher...")
        teacher = db.query(models.User).filter(models.User.phone == "13800000001").first()
        if not teacher:
            teacher = models.User(
                phone="13800000001",
                name="张老师",
                role="teacher",
                password_hash=auth.get_password_hash("teacher123")
            )
            db.add(teacher)
            db.commit()
            db.refresh(teacher)
            print(f"✅ Created teacher: {teacher.name} (ID: {teacher.id})")
        else:
            print(f"✅ Teacher already exists: {teacher.name} (ID: {teacher.id})")
        
        # 2. Create Classes
        print("\n🏫 Creating classes...")
        classes_data = [
            {"name": "2021级体育1班"},
            {"name": "2021级体育2班"},
            {"name": "2022级体育1班"}
        ]
        
        classes = []
        for cls_data in classes_data:
            cls = db.query(models.Class).filter(models.Class.name == cls_data["name"]).first()
            if not cls:
                cls = models.Class(
                    name=cls_data["name"],
                    teacher_id=teacher.id
                )
                db.add(cls)
                db.commit()
                db.refresh(cls)
                print(f"✅ Created class: {cls.name} (ID: {cls.id})")
            else:
                print(f"✅ Class already exists: {cls.name} (ID: {cls.id})")
            classes.append(cls)
        
        # 3. Create Students
        print("\n👥 Creating students...")
        student_names = [
            "李明", "王芳", "张伟", "刘洋", "陈静",
            "杨帆", "赵敏", "孙强", "周杰", "吴磊",
            "郑云", "王涛", "李娜", "张鹏", "刘畅",
            "陈浩", "杨雪", "赵刚", "孙丽", "周敏",
            "吴强", "郑芳", "王磊", "李涛", "张静",
            "刘伟", "陈明", "杨洋", "赵娜", "孙鹏",
            "周畅", "吴浩", "郑雪", "王刚", "李丽",
            "张敏", "刘强", "陈芳", "杨磊", "赵涛",
            "孙静", "周伟", "吴明", "郑洋", "王娜",
            "李鹏", "张畅", "刘浩", "陈雪", "杨刚"
        ]
        
        health_statuses = ["normal"] * 45 + ["leave"] * 3 + ["injured"] * 2
        random.shuffle(health_statuses)
        
        groups = ["A组", "B组", "C组", "D组"]
        
        students = []
        for i in range(50):
            student_id = f"20210{i+1:03d}"
            phone = f"138{i+1:08d}"
            
            existing_student = db.query(models.User).filter(models.User.phone == phone).first()
            if existing_student:
                students.append(existing_student)
                continue
            
            # Distribute students across classes
            class_idx = i % len(classes)
            
            student = models.User(
                phone=phone,
                name=student_names[i],
                role="student",
                password_hash=auth.get_password_hash("student123"),
                student_id=student_id,
                class_id=classes[class_idx].id,
                health_status=health_statuses[i],
                abnormal_reason="请假" if health_statuses[i] == "leave" else ("受伤" if health_statuses[i] == "injured" else None),
                group_name=groups[i % len(groups)]
            )
            db.add(student)
            students.append(student)
        
        db.commit()
        print(f"✅ Created/verified {len(students)} students")
        
        # Refresh all students to get IDs
        for student in students:
            db.refresh(student)
        
        # 4. Create Activities (Running records)
        print("\n🏃 Creating activity records...")
        activity_count = 0
        
        # Create activities for the past 7 days
        for day_offset in range(7):
            date = datetime.utcnow() - timedelta(days=day_offset)
            
            # Random number of students exercise each day (30-45 students)
            num_students = random.randint(30, 45)
            selected_students = random.sample(students, num_students)
            
            for student in selected_students:
                # Skip students with abnormal health status
                if student.health_status != "normal":
                    continue
                
                # Random activity type
                activity_type = random.choice(["run", "run", "run", "test"])  # More runs than tests
                
                # Random start time during the day
                start_hour = random.randint(6, 20)
                start_minute = random.randint(0, 59)
                started_at = date.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
                
                if activity_type == "run":
                    # Running activity
                    duration = random.randint(1200, 2400)  # 20-40 minutes in seconds
                    distance = round(random.uniform(2.0, 5.0), 2)  # 2-5 km
                    pace_seconds = int(duration / distance / 60)
                    pace = f"{pace_seconds // 60}'{pace_seconds % 60}\""
                    
                    activity = models.Activity(
                        user_id=student.id,
                        type="run",
                        source="free",
                        status="finished",
                        started_at=started_at,
                        ended_at=started_at + timedelta(seconds=duration)
                    )
                    db.add(activity)
                    db.flush()
                    
                    metrics = models.ActivityMetrics(
                        activity_id=activity.id,
                        distance=distance,
                        duration=duration,
                        pace=pace,
                        qualified=distance >= 2.0 and duration >= 1200
                    )
                    db.add(metrics)
                    
                else:
                    # Test activity
                    duration = random.randint(300, 600)  # 5-10 minutes
                    count = random.randint(1, 3)
                    
                    activity = models.Activity(
                        user_id=student.id,
                        type="test",
                        source="free",
                        status="finished",
                        started_at=started_at,
                        ended_at=started_at + timedelta(seconds=duration)
                    )
                    db.add(activity)
                    db.flush()
                    
                    metrics = models.ActivityMetrics(
                        activity_id=activity.id,
                        duration=duration,
                        count=count,
                        qualified=count >= 1
                    )
                    db.add(metrics)
                
                activity_count += 1
        
        db.commit()
        print(f"✅ Created {activity_count} activity records")
        
        # 5. Create Health Requests
        print("\n🏥 Creating health requests...")
        abnormal_students = [s for s in students if s.health_status != "normal"]
        
        for student in abnormal_students[:3]:  # Create pending requests for first 3
            existing_req = db.query(models.HealthRequest).filter(
                models.HealthRequest.student_id == student.id
            ).first()
            
            if not existing_req:
                req_type = "leave" if student.health_status == "leave" else "injury"
                health_req = models.HealthRequest(
                    student_id=student.id,
                    type=req_type,
                    reason=student.abnormal_reason or "身体不适",
                    status="pending"
                )
                db.add(health_req)
        
        db.commit()
        print(f"✅ Created health requests for abnormal students")
        
        # 6. Create Tasks
        print("\n📋 Creating tasks...")
        tasks_data = [
            {
                "title": "本周跑步任务",
                "type": "run",
                "min_distance": 3.0,
                "min_duration": 20,
                "deadline": datetime.utcnow() + timedelta(days=3),
                "description": "完成3公里跑步，时长不少于20分钟",
                "target_group": "all"
            },
            {
                "title": "体能测试",
                "type": "test",
                "min_count": 2,
                "deadline": datetime.utcnow() + timedelta(days=7),
                "description": "完成2次体能测试",
                "target_group": "all"
            }
        ]
        
        for task_data in tasks_data:
            existing_task = db.query(models.Task).filter(
                models.Task.title == task_data["title"]
            ).first()
            
            if not existing_task:
                task = models.Task(
                    **task_data,
                    created_by=teacher.id,
                    class_id=classes[0].id
                )
                db.add(task)
        
        db.commit()
        print(f"✅ Created tasks")
        
        # 7. Create Checkpoints
        print("\n📍 Creating checkpoints...")
        checkpoints_data = [
            {"name": "操场起点", "latitude": 39.9042, "longitude": 116.4074, "radius": 50},
            {"name": "体育馆", "latitude": 39.9052, "longitude": 116.4084, "radius": 50},
            {"name": "图书馆", "latitude": 39.9062, "longitude": 116.4094, "radius": 50}
        ]
        
        for cp_data in checkpoints_data:
            existing_cp = db.query(models.Checkpoint).filter(
                models.Checkpoint.name == cp_data["name"]
            ).first()
            
            if not existing_cp:
                checkpoint = models.Checkpoint(**cp_data)
                db.add(checkpoint)
        
        db.commit()
        print(f"✅ Created checkpoints")
        
        # 8. Create Sample Courses (Skip if table has issues)
        print("\n📚 Skipping course creation (table schema issues)...")
        
        # 9. Create Run Groups and Activities
        print("\n🏃 Creating run groups and activities...")
        
        run_groups_data = [
            {
                "name": "晨跑联盟",
                "description": "每天早上6点集合，一起晨跑",
                "avatar": "/static/group_morning.jpg",
                "total_mileage": 1250.5
            },
            {
                "name": "夜跑俱乐部",
                "description": "夜晚跑步，享受城市夜景",
                "avatar": "/static/group_night.jpg",
                "total_mileage": 980.3
            },
            {
                "name": "马拉松训练营",
                "description": "专业马拉松训练，冲击全马",
                "avatar": "/static/group_marathon.jpg",
                "total_mileage": 2100.8
            }
        ]
        
        run_groups = []
        for idx, group_data in enumerate(run_groups_data):
            existing_group = db.query(models.RunGroup).filter(
                models.RunGroup.name == group_data["name"]
            ).first()
            
            if not existing_group:
                creator = random.choice(students[:10])
                
                group = models.RunGroup(
                    **group_data,
                    creator_id=creator.id
                )
                db.add(group)
                db.flush()
                
                creator_member = models.RunGroupMember(
                    group_id=group.id,
                    user_id=creator.id,
                    role="creator",
                    total_mileage=group_data["total_mileage"] * 0.3
                )
                db.add(creator_member)
                
                num_members = random.randint(5, 10)
                available_students = [s for s in students if s.id != creator.id]
                members = random.sample(available_students, num_members)
                
                for member_student in members:
                    member = models.RunGroupMember(
                        group_id=group.id,
                        user_id=member_student.id,
                        role="member",
                        total_mileage=round(random.uniform(10.0, 100.0), 1)
                    )
                    db.add(member)
                
                group.member_count = num_members + 1
                print(f"✅ Created run group: {group_data['name']} with {group.member_count} members")
            else:
                group = existing_group
                print(f"✅ Run group already exists: {group_data['name']}")
            
            run_groups.append(group)
        
        db.commit()
        
        print("\n📅 Creating run group activities...")
        for group in run_groups:
            num_activities = random.randint(2, 3)
            
            for i in range(num_activities):
                days_ahead = random.randint(1, 7)
                activity_time = datetime.utcnow() + timedelta(days=days_ahead, hours=random.randint(6, 20))
                
                activity_titles = [
                    f"{group.name} - 周末长跑",
                    f"{group.name} - 晨跑打卡",
                    f"{group.name} - 夜跑活动",
                    f"{group.name} - 环校跑"
                ]
                
                activity_title = activity_titles[i % len(activity_titles)]
                
                existing_activity = db.query(models.RunGroupActivity).filter(
                    models.RunGroupActivity.group_id == group.id,
                    models.RunGroupActivity.title == activity_title
                ).first()
                
                if not existing_activity:
                    activity = models.RunGroupActivity(
                        group_id=group.id,
                        title=activity_title,
                        description=f"一起跑步，享受运动的乐趣！",
                        activity_time=activity_time,
                        location="校园操场",
                        distance=round(random.uniform(3.0, 10.0), 1),
                        total_quota=random.randint(20, 50),
                        apply_count=0,
                        status="upcoming",
                        created_by=group.creator_id
                    )
                    db.add(activity)
                    db.flush()
                    
                    group_members = db.query(models.RunGroupMember).filter(
                        models.RunGroupMember.group_id == group.id
                    ).all()
                    
                    num_applicants = min(random.randint(3, 8), len(group_members))
                    applicants = random.sample(group_members, num_applicants)
                    
                    for applicant in applicants:
                        application = models.RunGroupActivityApplication(
                            activity_id=activity.id,
                            user_id=applicant.user_id,
                            status="applied"
                        )
                        db.add(application)
                    
                    activity.apply_count = num_applicants
                    print(f"✅ Created activity: {activity.title} with {num_applicants} applicants")
        
        db.commit()
        print(f"✅ Created {len(run_groups)} run groups with activities")
        
        # Print summary
        print("\n" + "="*50)
        print("✨ Database seeding completed successfully!")
        print("="*50)
        print(f"\n📊 Summary:")
        print(f"  - Teachers: 1")
        print(f"  - Classes: {len(classes)}")
        print(f"  - Students: {len(students)}")
        print(f"  - Activities: {activity_count}")
        print(f"  - Abnormal Students: {len(abnormal_students)}")
        print(f"  - Tasks: {len(tasks_data)}")
        print(f"  - Checkpoints: {len(checkpoints_data)}")
        print(f"  - Run Groups: {len(run_groups)}")
        print(f"\n🔑 Login Credentials:")
        print(f"  Teacher: 13800000001 / teacher123")
        print(f"  Student: 13800000001 / student123 (or any 138xxxxxxxx)")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Campus Sports Health System - Database Seeder")
    print("="*50)
    seed_database()
