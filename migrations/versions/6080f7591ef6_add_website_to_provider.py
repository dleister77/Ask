"""add website to provider

Revision ID: 6080f7591ef6
Revises: e284826a33e3
Create Date: 2019-10-17 12:44:53.591706

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6080f7591ef6'
down_revision = 'e284826a33e3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('provider', sa.Column('website', sa.String(length=30), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('provider', 'website')
    # ### end Alembic commands ###
