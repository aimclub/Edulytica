"""Drop unique index on users.email

Revision ID: d8d3c0658591
Revises: b8a3c9d074aa
Create Date: 2025-05-01 23:52:56.222250

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd8d3c0658591'
down_revision: Union[str, None] = 'b8a3c9d074aa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index('ix_users_email', table_name='users')


def downgrade() -> None:
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
