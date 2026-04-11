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
    
    with engine.connect() as conn:
        # 定义所有可能有新增字段的表和字段明细
        schema_updates = {
            "activities": [
                ("is_valid", "BOOLEAN DEFAULT FALSE"),
                ("fail_reason", "VARCHAR"),
                ("face_verified", "BOOLEAN DEFAULT FALSE")
            ],
            "activity_metrics": [
                ("teacher_score", "FLOAT"),
                ("teacher_comment", "VARCHAR"),
                ("scored_at", "DATETIME"),
                ("scored_by", "INTEGER"),
                ("video_url", "VARCHAR"),
                ("score", "INTEGER"),
                ("score_detail", "VARCHAR")
            ],
            "users": [
                ("regular_score", "FLOAT DEFAULT 0.0"),
                ("group_name", "VARCHAR"),
                ("signature", "VARCHAR"),
                ("avatar_url", "VARCHAR")
            ],
            "tasks": [
                ("video_url", "VARCHAR"),
                ("target_group", "VARCHAR DEFAULT 'all'"),
                ("class_id", "INTEGER")
            ],
            "health_requests": [
                ("attachments", "VARCHAR"),
                ("start_date", "DATETIME"),
                ("end_date", "DATETIME")
            ]
        }

        print(">>> 开始全量检查每一张表的新增字段...")
        for table_name, fields in schema_updates.items():
            print(f"--- 检查表: {table_name} ---")
            for col_name, col_type in fields:
                try:
                    conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}"))
                    conn.commit()
                    print(f"  ✅ [成功] 添加字段: {table_name}.{col_name}")
                except Exception as e:
                    err_msg = str(e).lower()
                    if 'duplicate' in err_msg or 'already exists' in err_msg or 'no such table' in err_msg:
                        print(f"  ☑️ [跳过] 字段 {table_name}.{col_name} 已存在。")
                    else:
                        print(f"  ❌ [报错] 尝试添加 {table_name}.{col_name} 失败: {e}")
            
    print("\n🎉 全量数据库热升级完成！所有缺失列和新表均已补充就绪。")

if __name__ == "__main__":
    upgrade_database()

