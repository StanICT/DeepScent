"""Add is_admin field to User

Revision ID: 3a7c8839769a
Revises: 5e3a7e8e8c87
Create Date: 2026-05-01 13:38:15.054336

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3a7c8839769a'
down_revision = '5e3a7e8e8c87'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_admin', sa.Boolean(), nullable=False, server_default="0"))


    # ### end Alembic commands ###


def downgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('is_admin')


    op.create_table('_alembic_tmp_product',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=100), nullable=False),
    sa.Column('price', sa.FLOAT(), nullable=False),
    sa.Column('image', sa.VARCHAR(length=100), nullable=False),
    sa.Column('description', sa.TEXT(), nullable=False),
    sa.Column('brand', sa.VARCHAR(length=50), nullable=False),
    sa.Column('stock', sa.INTEGER(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
