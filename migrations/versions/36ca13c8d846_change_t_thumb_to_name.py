"""change t thumb to name

Revision ID: 36ca13c8d846
Revises: a467f30db5ca
Create Date: 2019-11-01 12:41:33.244525

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '36ca13c8d846'
down_revision = 'a467f30db5ca'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('picture', sa.Column('name', sa.String(length=120), nullable=False))
    op.drop_column('picture', 'thumb')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('picture', sa.Column('thumb', mysql.VARCHAR(collation='utf8_bin', length=120), nullable=False))
    op.drop_column('picture', 'name')
    # ### end Alembic commands ###
