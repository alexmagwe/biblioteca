"""empty message

Revision ID: 881a8153440d
Revises: ba370a82c8a7
Create Date: 2021-08-31 20:11:54.380150

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '881a8153440d'
down_revision = 'ba370a82c8a7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('username', sa.String(length=30), nullable=True))
        batch_op.create_index(batch_op.f('ix_users_username'), ['username'], unique=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_username'))
        batch_op.drop_column('username')

    # ### end Alembic commands ###