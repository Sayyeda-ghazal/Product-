"""add role column to table

Revision ID: 7b9ed4a9ed08
Revises: 08cc8def537b
Create Date: 2025-01-28 10:08:52.125651

"""
from typing import Sequence, Union
from sqlalchemy import Enum, Column
from alembic import op
import sqlalchemy as sa
from models import Roles


# revision identifiers, used by Alembic.
revision: str = '7b9ed4a9ed08'
down_revision: Union[str, None] = '08cc8def537b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', 
        Column('role', Enum(Roles), nullable=False, server_default='user')
    )


def downgrade() -> None:
    op.drop_column('your_table_name', 'role')
