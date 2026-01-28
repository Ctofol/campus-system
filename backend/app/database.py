from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 默认数据库连接地址，请根据实际情况修改
# 格式: postgresql://username:password@host:port/dbname
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:Chen20070509@localhost:5432/campus_db"

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
