"""create user table

Revision ID: cba5ac9bda10
Revises: 
Create Date: 2026-08-03 20:37:43.869572

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cba5ac9bda10'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'user',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(64), nullable=False),
        sa.Column('username', sa.String(32), nullable=False)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('user')
