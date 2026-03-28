import sys
import os
import random
from datetime import datetime, timedelta

# Add parent directory to sys.path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import models, database, auth
from sqlalchemy.orm import Session

def inject_data():
    db: Session = database.SessionLocal()
    
    # 1. Clear existing data (optional, but good for a clean test)
    # db.query(models.ActivityMetrics).delete()
    # db.query(models.ActivityEvidence).delete()
    # db.query(models.Activity).delete()
    # db.query(models.HealthRequest).delete()
    # db.query(models.Task).delete()
    # db.query(models.TeacherSubject).delete()
    # db.query(models.User).filter(models.User.role != 'admin').delete()
    # db.query(models.Class).delete()
    # db.query(models.Major).delete()
    # db.query(models.StudentProfile).delete()
    # db.commit()

    print("Cleaning database...")
    # Using more surgical cleaning to avoid deleting the admin user if it exists
    models.Base.metadata.drop_all(bind=database.engine)
    models.Base.metadata.create_all(bind=database.engine)
    
    # 2. Create Majors
    print("Creating majors...")
    majors = ["信息安全", "刑事技术", "网络工程", "治安管理"]
    major_objs = []
    for m_name in majors:
        major = models.Major(name=m_name)
        db.add(major)
        major_objs.append(major)
    db.flush() # Get IDs

    # 3. Create Classes for each Major
    print("Creating classes...")
    class_objs = []
    for major in major_objs:
        for i in range(1, 4):
            cls = models.Class(name=f"{i}区", major_id=major.id)
            db.add(cls)
            class_objs.append(cls)
    db.flush()

    # 4. Create Subjects
    print("Subjects: 篮球, 羽毛球, 乒乓球, 游泳, 跆拳道")
    subjects = ["篮球", "羽毛球", "乒乓球", "游泳", "跆拳道"]

    # 5. Create Admin (if not exists)
    print("Ensuring admin...")
    admin_hash = auth.get_password_hash("admin123")
    admin = models.User(
        name="管理员",
        phone="admin",
        password_hash=admin_hash,
        role="admin"
    )
    db.add(admin)

    # 6. Create Teachers
    print("Creating teachers...")
    teacher_objs = []
    for i in range(1, 6):
        t_hash = auth.get_password_hash("123456")
        teacher = models.User(
            name=f"老师{i}",
            phone=f"1380000000{i}",
            password_hash=t_hash,
            role="teacher"
        )
        db.add(teacher)
        teacher_objs.append(teacher)
    db.flush()

    # 7. Bind Teachers to Subjects
    for teacher in teacher_objs:
        # Each teacher manages 1 or 2 subjects
        assigned = random.sample(subjects, k=random.randint(1, 2))
        for sub in assigned:
            ts = models.TeacherSubject(teacher_id=teacher.id, subject_name=sub)
            db.add(ts)

    # 8. Create Students and Profiles
    print("Creating students...")
    student_counter = 1
    for cls in class_objs:
        # 10 students per class
        major = db.query(models.Major).filter(models.Major.id == cls.major_id).first()
        for i in range(1, 11):
            s_name = f"学生_{major.name}_{cls.name}_{i}"
            s_phone = f"1390000{student_counter:04d}"
            s_id = f"2024{student_counter:04d}"
            s_hash = auth.get_password_hash("123456")
            s_subject = random.choice(subjects)
            
            # Create Profile first
            profile = models.StudentProfile(
                student_id=s_id,
                full_name=s_name,
                gender=random.choice(["male", "female"]),
                class_name=cls.name,
                major=major.name,
                subject=s_subject,
                is_activated=True
            )
            db.add(profile)
            
            # Create User
            student = models.User(
                name=s_name,
                phone=s_phone,
                password_hash=s_hash,
                role="student",
                student_id=s_id,
                class_id=cls.id,
                major_id=major.id,
                major_name=major.name,
                subject=s_subject,
                health_status="normal"
            )
            db.add(student)
            db.flush() # Ensure student.id is generated for associations
            
            # Add more activities for common students to show dashboard statistics
            if random.random() > 0.1: # 90% students have activities
                # Simulate activities over the last 30 days
                for d in range(30):
                    # Randomly skip days or do 1-2 activities
                    if random.random() > 0.4: # 60% chance to have a run on that day
                        h_offset = random.randint(1, 4) if d == 0 else random.randint(6, 20)
                        start = datetime.utcnow() - timedelta(days=d, hours=h_offset)
                        duration = random.randint(900, 2400) # 15-40 min
                        distance = round(random.uniform(2.0, 5.0), 2)
                        
                        db_act = models.Activity(
                            user_id=student.id,
                            type="run",
                            source="free",
                            status="finished",
                            started_at=start,
                            ended_at=start + timedelta(seconds=duration),
                            is_valid=True,
                            face_verified=True
                        )
                        db.add(db_act)
                        db.flush()
                        
                        db_metrics = models.ActivityMetrics(
                            activity_id=db_act.id,
                            distance=distance,
                            duration=duration,
                            step_count=random.randint(3000, 8000),
                            pace=f"{int(duration / 60 / distance)}'{int((duration / 60 / distance % 1) * 60):02d}\"",
                            qualified=True # Mark as qualified for stats
                        )
                        db.add(db_metrics)
            
            # 5% chance of health request for data simulation
            if random.random() < 0.1: # Increased to 10%
                hr = models.HealthRequest(
                    student_id=student.id,
                    type=random.choice(["leave", "sick", "injury"]),
                    reason=f"{random.choice(['感冒', '拉肚子', '脚扭伤', '发烧'])}请假",
                    status="pending",
                    start_date=datetime.utcnow().date(),
                    end_date=datetime.utcnow().date() + timedelta(days=2),
                    created_at=datetime.utcnow()
                )
                db.add(hr)

            student_counter += 1

    # 9. Create some universal tasks
    print("Creating tasks...")
    for t in teacher_objs:
        task = models.Task(
            title=f"{random.choice(subjects)}专项训练",
            type="run",
            min_distance=2.0,
            min_duration=600,
            deadline=datetime.utcnow() + timedelta(days=7),
            description="请按时完成本周训练任务",
            created_by=t.id
        )
        db.add(task)

    db.commit()
    print(f"Injection complete! Created {student_counter-1} students, {len(teacher_objs)} teachers, {len(major_objs)} majors.")

if __name__ == "__main__":
    inject_data()
