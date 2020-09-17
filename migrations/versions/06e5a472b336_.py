"""empty message

Revision ID: 06e5a472b336
Revises: 1218efcccfbc
Create Date: 2020-09-17 10:55:17.330674

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '06e5a472b336'
down_revision = '1218efcccfbc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('teachers', schema=None) as batch_op:
        batch_op.drop_index('ix_teachers_email')

    op.drop_table('teachers')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('teachers',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('email', sa.VARCHAR(length=30), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    with op.batch_alter_table('teachers', schema=None) as batch_op:
        batch_op.create_index('ix_teachers_email', ['email'], unique=False)

    # ### end Alembic commands ###
