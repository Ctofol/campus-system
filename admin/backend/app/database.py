import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 默认使用项目根 backend 下的数据库，与管理端/学生教师端共用同一库
if os.getenv("SQLALCHEMY_DATABASE_URL"):
    SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")
else:
    _root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    _db_path = os.path.join(_root, "backend", "campus_sports.db")
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{_db_path}"

connect_args = {}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
