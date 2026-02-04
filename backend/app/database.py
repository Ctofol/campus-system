import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 默认数据库连接地址，优先从环境变量获取
# 格式: postgresql://username:password@host:port/dbname
DEFAULT_DB_URL = "postgresql://postgres:Chen20070509@localhost:5432/campus_db"
SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL", DEFAULT_DB_URL)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
