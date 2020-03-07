"""message column name changes

Revision ID: 3221bb685e15
Revises: 09d0788a9f2d
Create Date: 2020-03-04 07:30:57.288219

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '3221bb685e15'
down_revision = '09d0788a9f2d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('message_user', sa.Column('_full_name', sa.String(length=128), nullable=True))
    op.add_column('message_user', sa.Column('_tag', sa.String(length=20), nullable=True))
    op.add_column('message_user', sa.Column('email', sa.String(length=120), nullable=True))
    op.create_index(op.f('ix_message_user__tag'), 'message_user', ['_tag'], unique=False)
    op.drop_index('ix_message_user__status', table_name='message_user')
    op.drop_column('message_user', 'user_email')
    op.drop_column('message_user', '_status')
    op.drop_column('message_user', 'user_name')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('message_user', sa.Column('user_name', mysql.VARCHAR(collation='utf8_bin', length=128), nullable=True))
    op.add_column('message_user', sa.Column('_status', mysql.VARCHAR(collation='utf8_bin', length=20), nullable=True))
    op.add_column('message_user', sa.Column('user_email', mysql.VARCHAR(collation='utf8_bin', length=120), nullable=True))
    op.create_index('ix_message_user__status', 'message_user', ['_status'], unique=False)
    op.drop_index(op.f('ix_message_user__tag'), table_name='message_user')
    op.drop_column('message_user', 'email')
    op.drop_column('message_user', '_tag')
    op.drop_column('message_user', '_full_name')
    # ### end Alembic commands ###
