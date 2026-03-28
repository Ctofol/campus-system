from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import hashlib
from .. import models, schemas, auth, database, config

router = APIRouter(prefix="/auth", tags=["auth"])

get_db = database.get_db

@router.post("/register", response_model=schemas.Token)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    注册逻辑：学生采用“档案激活”模式。
    """
    # 1. Verify Captcha
    verify_src = user.captcha_code.upper() + config.CAPTCHA_SECRET
    expected_key = hashlib.md5(verify_src.encode("utf-8")).hexdigest()
    if expected_key != user.captcha_key:
        raise HTTPException(status_code=400, detail="验证码错误")

    # 2. 手机号唯一
    db_user = db.query(models.User).filter(models.User.phone == user.phone).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Phone already registered")

    hashed_password = auth.get_password_hash(user.password)

    # 3. 学生：走档案激活流程
    if user.role == "student":
        if not user.student_id:
            raise HTTPException(status_code=400, detail="学生注册必须提供学号")

        profile = db.query(models.StudentProfile).filter(
            models.StudentProfile.student_id == user.student_id
        ).first()
        if not profile:
            raise HTTPException(status_code=403, detail="档案库中无此信息，请联系管理员")

        if profile.full_name.strip() != user.name.strip():
            raise HTTPException(status_code=403, detail="姓名与档案不符，请确认后重试")

        if profile.is_activated:
            raise HTTPException(status_code=400, detail="该学号已被注册")

        # 根据档案中的内容找到对应的专业和班级
        db_major = db.query(models.Major).filter(models.Major.name == profile.major).first()
        if not db_major:
            db_major = models.Major(name=profile.major)
            db.add(db_major)
            db.commit()
            db.refresh(db_major)

        db_class = db.query(models.Class).filter(
            models.Class.name == profile.class_name, 
            models.Class.major_id == db_major.id
        ).first()
        if not db_class:
            db_class = models.Class(name=profile.class_name, major_id=db_major.id)
            db.add(db_class)
            db.commit()
            db.refresh(db_class)

        new_user = models.User(
            phone=user.phone,
            name=profile.full_name,
            role="student",
            password_hash=hashed_password,
            student_id=profile.student_id,
            gender=profile.gender,
            class_id=db_class.id,
            major_id=db_major.id,
            major_name=profile.major,
            subject=profile.subject,
        )
        db.add(new_user)
        profile.is_activated = True
        db.commit()
        db.refresh(new_user)

    else:
        new_user = models.User(
            phone=user.phone,
            name=user.name,
            role=user.role,
            password_hash=hashed_password,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

    access_token = auth.create_access_token(
        data={"sub": new_user.phone, "role": new_user.role}
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": new_user.role,
        "user_id": new_user.id,
        "name": new_user.name,
        "class_name": new_user.class_name,
        "class_id": new_user.class_id,
        "student_id": new_user.student_id,
        "major": new_user.major,
        "major_id": new_user.major_id,
        "subject": new_user.subject,
    }

@router.post("/login", response_model=schemas.Token)
def login(user_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.phone == user_data.phone).first()
    if not user or not auth.verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect phone or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth.create_access_token(
        data={"sub": user.phone, "role": user.role}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "user_id": user.id,
        "name": user.name,
        "class_name": user.class_name,
        "class_id": user.class_id,
        "student_id": user.student_id,
        "major": user.major,
        "major_id": user.major_id,
        "subject": user.subject,
    }

@router.post("/refresh")
def refresh_token(current_user: models.User = Depends(auth.get_current_user)):
    access_token = auth.create_access_token(
        data={"sub": current_user.phone, "role": current_user.role}
    )
    return {"access_token": access_token, "token_type": "bearer"}
