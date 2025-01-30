"""add owner_id to PIMS table

Revision ID: 919eb0f9f838
Revises: 7b9ed4a9ed08
Create Date: 2025-01-28 10:50:53.721677

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '919eb0f9f838'
down_revision: Union[str, None] = '7b9ed4a9ed08'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('pims', sa.Column('owner_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_owner_id",  # Foreign key name
        "pims",  # Source table
        "users",  # Target table
        ["owner_id"],  # Source column
        ["id"],  # Target column
    )


def downgrade() -> None:
    op.drop_constraint("fk_owner_id", "pims", type_="foreignkey")
    op.drop_column('pims', 'owner_id')
