"""employee full name

Revision ID: 57a71507107f
Revises: 416d497d4edb
Create Date: 2023-08-19 14:00:02.719971

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '57a71507107f'
down_revision: Union[str, None] = '416d497d4edb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('employee', 'name', new_column_name='first_name')
    op.add_column(
        'employee',
        sa.Column('last_name', sa.String(length=127), nullable=True),
    )


def downgrade() -> None:
    op.alter_column('employee', 'first_name', new_column_name='name')
    op.drop_column('employee', 'last_name')
