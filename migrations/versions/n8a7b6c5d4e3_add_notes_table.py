"""Add notes table and product note relationship

Revision ID: n8a7b6c5d4e3
Revises: m1e8f2d3c4b5
Create Date: 2026-05-16 01:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'n8a7b6c5d4e3'
down_revision = 'm1e8f2d3c4b5'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    note_exists = bind.execute(sa.text("SELECT name FROM sqlite_master WHERE type='table' AND name='note'")).fetchone()
    if not note_exists:
        op.create_table(
            'note',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('name', sa.String(length=100), nullable=False, unique=True),
            sa.Column('image', sa.String(length=100), nullable=True)
        )

    product_columns = [row[1] for row in bind.execute(sa.text("PRAGMA table_info(product)")).fetchall()]
    if 'note_id' not in product_columns:
        with op.batch_alter_table('product', schema=None) as batch_op:
            batch_op.add_column(sa.Column('note_id', sa.Integer(), nullable=True))
            batch_op.create_foreign_key('fk_product_note', 'note', ['note_id'], ['id'])


def downgrade():
    bind = op.get_bind()
    product_columns = [row[1] for row in bind.execute(sa.text("PRAGMA table_info(product)")).fetchall()]
    if 'note_id' in product_columns:
        with op.batch_alter_table('product', schema=None) as batch_op:
            batch_op.drop_constraint('fk_product_note', type_='foreignkey')
            batch_op.drop_column('note_id')
    note_exists = bind.execute(sa.text("SELECT name FROM sqlite_master WHERE type='table' AND name='note'")).fetchone()
    if note_exists:
        op.drop_table('note')
