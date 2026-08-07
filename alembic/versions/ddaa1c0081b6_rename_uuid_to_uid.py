"""Rename uuid to uid

Revision ID: ddaa1c0081b6
Revises: 5986676e7ac8
Create Date: 2026-08-07 14:24:06.615530

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ddaa1c0081b6'
down_revision: Union[str, Sequence[str], None] = '5986676e7ac8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('user', 'uuid', new_column_name='uid')


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('user', 'uid', new_column_name='uuid')
