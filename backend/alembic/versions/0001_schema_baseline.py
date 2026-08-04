"""为当前 SQLAlchemy 模型建立兼容基线。

Revision ID: 0001_schema_baseline
Revises:
"""

from alembic import op

from app.database import Base
from app import models  # noqa: F401 - 填充 Base.metadata


revision = "0001_schema_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # create_all 对已有表无操作，对空数据库创建当前完整结构。
    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    # 基线可能接管已有数据库；自动删表不安全，因此有意保持为空。
    pass
