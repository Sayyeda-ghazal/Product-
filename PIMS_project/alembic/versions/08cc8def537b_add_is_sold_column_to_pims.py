"""add is_sold column to PIMS

Revision ID: 08cc8def537b
Revises: 
Create Date: 2025-01-24 13:10:10.408499

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '08cc8def537b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('pims', sa.Column('is_sold', sa.Boolean(), nullable=False, server_default=sa.false()))

def downgrade() -> None:
    pass
