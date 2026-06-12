"""
一键登录账号注入脚本 (standalone, no FastAPI dependency)
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base
import bcrypt

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DB_URL = f"sqlite:///{os.path.join(PROJECT_ROOT, 'campus_sports.db')}"

engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()




class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    role = Column(String, nullable=False)
    name = Column(String, nullable=False)
    phone = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=True)
    major_id = Column(Integer, ForeignKey("majors.id"), nullable=True)
    student_id = Column(String, ForeignKey("student_profiles.student_id"), unique=True, nullable=True)
    gender = Column(String, nullable=True)
    major_name = Column(String, nullable=True)
    subject = Column(String, nullable=True)
    health_status = Column(String, default="normal")
    abnormal_reason = Column(String, nullable=True)
    group_name = Column(String, nullable=True)
    signature = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    regular_score = Column(Float, default=0.0)


class StudentProfile(Base):
    __tablename__ = "student_profiles"
    student_id = Column(String, primary_key=True)
    full_name = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    class_name = Column(String, nullable=False)
    major = Column(String, nullable=True)
    subject = Column(String, nullable=True)
    is_activated = Column(Boolean, default=False)


class Major(Base):
    __tablename__ = "majors"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)


class Class(Base):
    __tablename__ = "classes"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    major_id = Column(Integer, ForeignKey("majors.id"), nullable=False)


class TeacherSubject(Base):
    __tablename__ = "teacher_subjects"
    id = Column(Integer, primary_key=True)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject_name = Column(String, nullable=False)


def get_password_hash(password: str) -> str:
    pwd = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(pwd, salt).decode('utf-8')


STUDENT_PHONE = '13800138000'
TEACHER_PHONE = '13900139000'
PASSWORD = '123456'
STUDENT_STUDENT_ID = '2024001'
STUDENT_NAME = '测试学生'
TEACHER_NAME = '测试教师'


def inject_student(db):
    user = db.query(User).filter(User.phone == STUDENT_PHONE).first()
    if user:
        print(f"学生账号已存在: {user.name} ({user.phone})")
        return user

    profile = db.query(StudentProfile).filter(
        StudentProfile.student_id == STUDENT_STUDENT_ID
    ).first()
    if not profile:
        profile = StudentProfile(
            student_id=STUDENT_STUDENT_ID,
            full_name=STUDENT_NAME,
            gender='male',
            class_name='人工智能协会 BU',
            major='人工智能',
            subject='篮球',
            is_activated=True
        )
        db.add(profile)
        print("已创建 StudentProfile")

    class_obj = db.query(Class).filter(Class.name == '人工智能协会 BU').first()
    major = db.query(Major).filter(Major.name == '人工智能').first()

    user = User(
        name=STUDENT_NAME,
        phone=STUDENT_PHONE,
        password_hash=get_password_hash(PASSWORD),
        role='student',
        student_id=STUDENT_STUDENT_ID,
        class_id=class_obj.id if class_obj else None,
        major_id=major.id if major else None,
        major_name='人工智能',
        gender='male',
        subject='篮球',
        health_status='normal'
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"已创建学生账号: {user.name} ({user.phone})")
    return user


def inject_teacher(db):
    user = db.query(User).filter(User.phone == TEACHER_PHONE).first()
    if user:
        print(f"教师账号已存在: {user.name} ({user.phone})")
        return user

    user = User(
        name=TEACHER_NAME,
        phone=TEACHER_PHONE,
        password_hash=get_password_hash(PASSWORD),
        role='teacher',
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    for sub in ["篮球", "羽毛球", "乒乓球"]:
        exists = db.query(TeacherSubject).filter(
            TeacherSubject.teacher_id == user.id,
            TeacherSubject.subject_name == sub,
        ).first()
        if not exists:
            db.add(TeacherSubject(teacher_id=user.id, subject_name=sub))
    db.commit()

    print(f"已创建教师账号: {user.name} ({user.phone})")
    return user


def main():
    db = SessionLocal()
    try:
        print("=" * 50)
        print("一键登录账号注入")
        print("=" * 50)
        inject_student(db)
        inject_teacher(db)
        print("\n注入完成！请使用以下账号一键登录：")
        print(f"  学生端: {STUDENT_PHONE} / {PASSWORD}")
        print(f"  教师端: {TEACHER_PHONE} / {PASSWORD}")
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == '__main__':
    main()
