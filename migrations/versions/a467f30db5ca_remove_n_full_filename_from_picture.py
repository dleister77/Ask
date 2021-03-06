"""remove n full filename from picture

Revision ID: a467f30db5ca
Revises: 0e6888c3db4f
Create Date: 2019-11-01 12:29:26.770226

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'a467f30db5ca'
down_revision = '0e6888c3db4f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('picture', 'name')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('picture', sa.Column('name', mysql.VARCHAR(collation='utf8_bin', length=120), nullable=False))
    # ### end Alembic commands ###
