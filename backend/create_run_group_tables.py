"""
创建跑团相关数据表
"""
from app.database import engine, Base
from app.models import RunGroup, RunGroupMember, RunGroupActivity, RunGroupActivityApplication

def create_tables():
    print("Creating run group tables...")
    Base.metadata.create_all(bind=engine, tables=[
        RunGroup.__table__,
        RunGroupMember.__table__,
        RunGroupActivity.__table__,
        RunGroupActivityApplication.__table__
    ])
    print("✓ Run group tables created successfully!")

if __name__ == "__main__":
    create_tables()
