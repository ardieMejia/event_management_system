"""empty message

Revision ID: b2f3a19d27d0
Revises: 92f05fb95060
Create Date: 2025-03-16 22:14:14.417857

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2f3a19d27d0'
down_revision = '92f05fb95060'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('event',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tournamentName', sa.String(length=128), nullable=True),
    sa.Column('startDate', sa.String(length=64), nullable=True),
    sa.Column('endDate', sa.String(length=64), nullable=True),
    sa.Column('discipline', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('event', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_event_discipline'), ['discipline'], unique=False)
        batch_op.create_index(batch_op.f('ix_event_endDate'), ['endDate'], unique=False)
        batch_op.create_index(batch_op.f('ix_event_startDate'), ['startDate'], unique=False)
        batch_op.create_index(batch_op.f('ix_event_tournamentName'), ['tournamentName'], unique=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('event', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_event_tournamentName'))
        batch_op.drop_index(batch_op.f('ix_event_startDate'))
        batch_op.drop_index(batch_op.f('ix_event_endDate'))
        batch_op.drop_index(batch_op.f('ix_event_discipline'))

    op.drop_table('event')
    # ### end Alembic commands ###
