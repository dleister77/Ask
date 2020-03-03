"""user m messages v1

Revision ID: 99cec7780657
Revises: 36ca13c8d846
Create Date: 2019-11-05 07:49:05.310994

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '99cec7780657'
down_revision = '36ca13c8d846'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('conversation',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_conversation'))
    )
    op.create_table('message',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('conversation_id', sa.Integer(), nullable=True),
    sa.Column('from_id', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('msg_type', sa.String(length=25), nullable=True),
    sa.Column('read', sa.Boolean(), nullable=True),
    sa.Column('subject', sa.String(length=50), nullable=True),
    sa.Column('body', sa.String(length=250), nullable=True),
    sa.ForeignKeyConstraint(['conversation_id'], ['conversation.id'], name=op.f('fk_message_conversation_id_conversation'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['from_id'], ['user.id'], name=op.f('fk_message_from_id_user')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_message'))
    )
    op.create_index(op.f('ix_message_msg_type'), 'message', ['msg_type'], unique=False)
    op.create_index(op.f('ix_message_read'), 'message', ['read'], unique=False)
    op.create_index(op.f('ix_message_subject'), 'message', ['subject'], unique=False)
    op.create_index(op.f('ix_message_timestamp'), 'message', ['timestamp'], unique=False)
    op.create_table('user_message',
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('message_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['message_id'], ['message.id'], name=op.f('fk_user_message_message_id_message')),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name=op.f('fk_user_message_user_id_user'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_message')
    op.drop_index(op.f('ix_message_timestamp'), table_name='message')
    op.drop_index(op.f('ix_message_subject'), table_name='message')
    op.drop_index(op.f('ix_message_read'), table_name='message')
    op.drop_index(op.f('ix_message_msg_type'), table_name='message')
    op.drop_table('message')
    op.drop_table('conversation')
    # ### end Alembic commands ###