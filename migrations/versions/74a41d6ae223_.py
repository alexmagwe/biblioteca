"""empty message

Revision ID: 74a41d6ae223
Revises: e2699ac12604
Create Date: 2021-02-19 23:11:35.636680

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '74a41d6ae223'
down_revision = 'e2699ac12604'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('notes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('size', sa.String(), nullable=True))
        batch_op.create_index(batch_op.f('ix_notes_size'), ['size'], unique=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('notes', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_notes_size'))
        batch_op.drop_column('size')

    # ### end Alembic commands ###
