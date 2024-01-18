"""init db

Revision ID: 1ca60b32bf67
Revises: 
Create Date: 2023-10-05 10:29:19.202761

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1ca60b32bf67'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('customer',
    sa.Column('customer_id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=127), nullable=False),
    sa.Column('last_name', sa.String(length=127), nullable=False),
    sa.Column('address', sa.String(length=255), nullable=False),
    sa.Column('email', sa.String(length=127), nullable=False),
    sa.PrimaryKeyConstraint('customer_id'),
    sa.UniqueConstraint('email')
    )
    op.create_index('customer_full_name', 'customer', ['first_name', 'last_name'], unique=False)
    op.create_table('employee',
    sa.Column('employee_id', sa.Integer(), nullable=False),
    sa.Column('manager_id', sa.Integer(), nullable=True),
    sa.Column('first_name', sa.String(length=127), nullable=False),
    sa.Column('last_name', sa.String(length=127), nullable=True),
    sa.Column('is_manager', sa.Boolean(), nullable=False),
    sa.Column('hire_date', sa.Date(), nullable=False),
    sa.ForeignKeyConstraint(['manager_id'], ['employee.employee_id'], ),
    sa.PrimaryKeyConstraint('employee_id')
    )
    op.create_table('product',
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('product_name', sa.String(length=255), nullable=False),
    sa.Column('unit_price', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('units_in_stock', sa.Integer(), nullable=False),
    sa.Column('type', sa.Enum('PHONE', 'ACCESSORY', 'OTHER', name='producttype'), nullable=False),
    sa.PrimaryKeyConstraint('product_id')
    )
    op.create_index(op.f('ix_product_product_name'), 'product', ['product_name'], unique=False)
    op.create_table('order',
    sa.Column('order_id', sa.Integer(), nullable=False),
    sa.Column('customer_id', sa.Integer(), nullable=False),
    sa.Column('employee_id', sa.Integer(), nullable=True),
    sa.Column('order_datetime', sa.DateTime(), nullable=False),
    sa.Column('is_shipped', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['customer_id'], ['customer.customer_id'], ),
    sa.ForeignKeyConstraint(['employee_id'], ['employee.employee_id'], ),
    sa.PrimaryKeyConstraint('order_id')
    )
    op.create_table('order_detail',
    sa.Column('order_id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['order_id'], ['order.order_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['product_id'], ['product.product_id'], ),
    sa.PrimaryKeyConstraint('order_id', 'product_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('order_detail')
    op.drop_table('order')
    op.drop_index(op.f('ix_product_product_name'), table_name='product')
    op.drop_table('product')
    op.drop_table('employee')
    op.drop_index('customer_full_name', table_name='customer')
    op.drop_table('customer')
    # ### end Alembic commands ###
