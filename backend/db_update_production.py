import os
import sys

# 将上一级目录加入环境变量以便导入
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.database import SQLALCHEMY_DATABASE_URL
from app.models import Base

def upgrade_database():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    # 1. 自动创建所有缺失的新表 (如跑团联盟相关表、课程相关表)
    print(">>> 正在扫描并创建缺失的数据表 (例如 run_groups, courses 等)...")
    Base.metadata.create_all(bind=engine)

    # 定义所有可能有新增字段的表和字段明细
    schema_updates = {
        "activities": [
            ("is_valid", "BOOLEAN DEFAULT FALSE"),
            ("fail_reason", "VARCHAR"),
            ("face_verified", "BOOLEAN DEFAULT FALSE"),
            ("task_id", "INTEGER"),
        ],
        "activity_metrics": [
            ("teacher_score", "FLOAT"),
            ("teacher_comment", "VARCHAR"),
            ("scored_at", "DATETIME"),
            ("scored_by", "INTEGER"),
            ("video_url", "VARCHAR"),
            ("score", "INTEGER"),
            ("score_detail", "VARCHAR"),
        ],
        "users": [
            ("health_status", "VARCHAR DEFAULT 'normal'"),
            ("abnormal_reason", "VARCHAR"),
            ("regular_score", "FLOAT DEFAULT 0.0"),
            ("group_name", "VARCHAR"),
            ("signature", "VARCHAR"),
            ("avatar_url", "VARCHAR"),
        ],
        "tasks": [
            ("video_url", "VARCHAR"),
            ("target_group", "VARCHAR DEFAULT 'all'"),
            ("class_id", "INTEGER"),
            ("starts_at", "DATETIME"),
        ],
        "health_requests": [
            ("attachments", "VARCHAR"),
            ("start_date", "DATETIME"),
            ("end_date", "DATETIME"),
        ],
    }

    print(">>> 开始全量检查每一张表的新增字段...")
    # 每条 ALTER 单独事务，避免 PostgreSQL 上「列已存在」失败后同连接后续语句 InFailedSqlTransaction
    for table_name, fields in schema_updates.items():
        print(f"--- 检查表: {table_name} ---")
        for col_name, col_type in fields:
            try:
                with engine.begin() as txconn:
                    txconn.execute(
                        text(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}")
                    )
                print(f"  [ok] added {table_name}.{col_name}")
            except Exception as e:
                err_msg = str(e).lower()
                if (
                    "duplicate" in err_msg
                    or "already exists" in err_msg
                    or "no such table" in err_msg
                ):
                    print(f"  [skip] {table_name}.{col_name} already exists")
                else:
                    print(f"  [err] {table_name}.{col_name}: {e}")

    print("\n[done] database schema check finished.")

if __name__ == "__main__":
    upgrade_database()

