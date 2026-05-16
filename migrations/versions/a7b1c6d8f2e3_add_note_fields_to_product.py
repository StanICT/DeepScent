"""Add note fields to Product

Revision ID: a7b1c6d8f2e3
Revises: 5e3a7e8e8c87
Create Date: 2026-05-16 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a7b1c6d8f2e3'
down_revision = '5e3a7e8e8c87'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.add_column(sa.Column('note_name', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('note_image', sa.String(length=100), nullable=True))


def downgrade():
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.drop_column('note_image')
        batch_op.drop_column('note_name')
