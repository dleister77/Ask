"""change provider.is_active to server side default

Revision ID: f55817922f06
Revises: 7a07e2d280bf
Create Date: 2020-04-04 07:23:59.748140

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'f55817922f06'
down_revision = '7a07e2d280bf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('message', 'conversation_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=False)
    op.alter_column('provider', 'is_active',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=False, server_default=sa.sql.expression.text('1'))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('provider', 'is_active',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=True)
    op.alter_column('message', 'conversation_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=True)
    # ### end Alembic commands ###
