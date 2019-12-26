"""mnessages v3

Revision ID: e94e80a00b04
Revises: e80119a86721
Create Date: 2019-12-22 10:24:57.622444

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'e94e80a00b04'
down_revision = 'e80119a86721'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('message', sa.Column('read', sa.Boolean(), nullable=True))
    op.add_column('message', sa.Column('status', sa.String(length=20), nullable=True))
    op.create_index(op.f('ix_message_read'), 'message', ['read'], unique=False)
    op.create_index(op.f('ix_message_status'), 'message', ['status'], unique=False)
    op.drop_index('ix_message_sender_status', table_name='message')
    op.drop_column('message', 'sender_status')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('message', sa.Column('sender_status', mysql.VARCHAR(collation='utf8_bin', length=20), nullable=True))
    op.create_index('ix_message_sender_status', 'message', ['sender_status'], unique=False)
    op.drop_index(op.f('ix_message_status'), table_name='message')
    op.drop_index(op.f('ix_message_read'), table_name='message')
    op.drop_column('message', 'status')
    op.drop_column('message', 'read')
    # ### end Alembic commands ###
