"""empty message

Revision ID: 19ac3eb5def8
Revises: 
Create Date: 2025-03-16 17:31:59.512547

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '19ac3eb5def8'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('event',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tournamentName', sa.String(length=128), nullable=False),
    sa.Column('startDate', sa.String(length=64), nullable=False),
    sa.Column('endDate', sa.String(length=64), nullable=False),
    sa.Column('discipline', sa.String(length=64), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('event', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_event_discipline'), ['discipline'], unique=False)
        batch_op.create_index(batch_op.f('ix_event_endDate'), ['endDate'], unique=False)
        batch_op.create_index(batch_op.f('ix_event_startDate'), ['startDate'], unique=False)
        batch_op.create_index(batch_op.f('ix_event_tournamentName'), ['tournamentName'], unique=True)

    op.create_table('member',
    sa.Column('mcfId', sa.Integer(), nullable=False),
    sa.Column('mcfName', sa.String(length=128), nullable=False),
    sa.Column('gender', sa.String(length=64), nullable=False),
    sa.Column('yearOfBirth', sa.String(length=64), nullable=False),
    sa.Column('state', sa.String(length=64), nullable=False),
    sa.Column('nationalRating', sa.String(length=64), nullable=False),
    sa.PrimaryKeyConstraint('mcfId')
    )
    with op.batch_alter_table('member', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_member_gender'), ['gender'], unique=False)
        batch_op.create_index(batch_op.f('ix_member_mcfName'), ['mcfName'], unique=False)
        batch_op.create_index(batch_op.f('ix_member_nationalRating'), ['nationalRating'], unique=False)
        batch_op.create_index(batch_op.f('ix_member_state'), ['state'], unique=False)
        batch_op.create_index(batch_op.f('ix_member_yearOfBirth'), ['yearOfBirth'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('member', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_member_yearOfBirth'))
        batch_op.drop_index(batch_op.f('ix_member_state'))
        batch_op.drop_index(batch_op.f('ix_member_nationalRating'))
        batch_op.drop_index(batch_op.f('ix_member_mcfName'))
        batch_op.drop_index(batch_op.f('ix_member_gender'))

    op.drop_table('member')
    with op.batch_alter_table('event', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_event_tournamentName'))
        batch_op.drop_index(batch_op.f('ix_event_startDate'))
        batch_op.drop_index(batch_op.f('ix_event_endDate'))
        batch_op.drop_index(batch_op.f('ix_event_discipline'))

    op.drop_table('event')
    # ### end Alembic commands ###
