from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from . import models, schemas, database, config

# 密钥配置通过 config 注入
SECRET_KEY = config.SECRET_KEY
ALGORITHM = config.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = config.ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)  # 允许可选认证

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    # Passlib bcrypt has a 72-character limit, truncating prevents errors
    password = password[:72]
    return pwd_context.hash(password)




def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_user_access_token(
    user: models.User,
    *,
    scope: str = "access",
    expires_delta: Optional[timedelta] = None,
):
    """签发以用户 ID 为主体的稳定令牌；手机号变化不再改变登录主体。"""

    return create_access_token(
        {
            "sub": str(user.id),
            "uid": user.id,
            "role": user.role,
            "ver": int(user.token_version or 0),
            "scope": scope,
        },
        expires_delta=expires_delta,
    )


def validate_new_password(password: str) -> str:
    value = (password or "").strip()
    if not 8 <= len(value) <= 20:
        raise ValueError("新密码长度须为 8–20 位")
    if not any(ch.isalpha() for ch in value) or not any(ch.isdigit() for ch in value):
        raise ValueError("新密码必须同时包含字母和数字")
    return value

async def get_current_user_allow_incomplete(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(database.get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("uid")
        subject: str = payload.get("sub")
        role: str = payload.get("role")
        if subject is None:
            raise credentials_exception
        token_data = schemas.TokenData(
            user_id=int(user_id) if user_id is not None else None,
            phone=subject if user_id is None else None,
            role=role,
            token_version=payload.get("ver"),
            scope=payload.get("scope"),
        )
    except (JWTError, TypeError, ValueError):
        raise credentials_exception
    if token_data.user_id is not None:
        user = db.query(models.User).filter(models.User.id == token_data.user_id).first()
    else:
        # 兼容升级前以手机号作为 sub 的存量令牌。
        user = db.query(models.User).filter(models.User.phone == token_data.phone).first()
    if user is None:
        raise credentials_exception
    if token_data.token_version is not None and int(user.token_version or 0) != token_data.token_version:
        raise credentials_exception
    if not bool(user.is_active):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="账号已停用，请联系管理员")
    return user


async def get_current_user(
    current_user: models.User = Depends(get_current_user_allow_incomplete),
):
    if current_user.must_change_password:
        raise HTTPException(status_code=403, detail="请先完成账号设置")
    return current_user

async def get_current_teacher(current_user: models.User = Depends(get_current_user)):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Not a teacher")
    return current_user
