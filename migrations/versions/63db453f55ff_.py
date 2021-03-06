"""empty message

Revision ID: 63db453f55ff
Revises: a41192e560d1
Create Date: 2020-05-25 23:28:42.804205

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '63db453f55ff'
down_revision = 'a41192e560d1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('courses',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=100), nullable=True),
    sa.Column('path', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('path')
    )
    with op.batch_alter_table('courses', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_courses_name'), ['name'], unique=True)

    op.create_table('teachers',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('email', sa.String(length=30), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    with op.batch_alter_table('teachers', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_teachers_email'), ['email'], unique=False)

    op.create_table('units',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('acronym', sa.String(length=10), nullable=True),
    sa.Column('path', sa.String(), nullable=True),
    sa.Column('semester', sa.String(length=10), nullable=True),
    sa.Column('year', sa.Integer(), nullable=True),
    sa.Column('courses_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['courses_id'], ['courses.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    with op.batch_alter_table('units', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_units_acronym'), ['acronym'], unique=True)
        batch_op.create_index(batch_op.f('ix_units_name'), ['name'], unique=True)
        batch_op.create_index(batch_op.f('ix_units_path'), ['path'], unique=True)
        batch_op.create_index(batch_op.f('ix_units_semester'), ['semester'], unique=False)
        batch_op.create_index(batch_op.f('ix_units_year'), ['year'], unique=False)

    op.create_table('users',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('email', sa.String(length=30), nullable=False),
    sa.Column('permissions', sa.Integer(), nullable=True),
    sa.Column('password', sa.String(length=100), nullable=True),
    sa.Column('course_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('id')
    )
    op.create_table('notes',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=100), nullable=True),
    sa.Column('unit_id', sa.Integer(), nullable=False),
    sa.Column('path', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['unit_id'], ['units.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    with op.batch_alter_table('notes', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_notes_name'), ['name'], unique=True)
        batch_op.create_index(batch_op.f('ix_notes_path'), ['path'], unique=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('notes', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_notes_path'))
        batch_op.drop_index(batch_op.f('ix_notes_name'))

    op.drop_table('notes')
    op.drop_table('users')
    with op.batch_alter_table('units', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_units_year'))
        batch_op.drop_index(batch_op.f('ix_units_semester'))
        batch_op.drop_index(batch_op.f('ix_units_path'))
        batch_op.drop_index(batch_op.f('ix_units_name'))
        batch_op.drop_index(batch_op.f('ix_units_acronym'))

    op.drop_table('units')
    with op.batch_alter_table('teachers', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_teachers_email'))

    op.drop_table('teachers')
    with op.batch_alter_table('courses', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_courses_name'))

    op.drop_table('courses')
    # ### end Alembic commands ###
