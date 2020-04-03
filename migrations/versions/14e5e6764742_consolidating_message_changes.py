"""consolidating message changes

Revision ID: 14e5e6764742
Revises: c8c1b223594e
Create Date: 2020-04-02 16:34:06.825061

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision = '14e5e6764742'
down_revision = 'c8c1b223594e'
branch_labels = None
depends_on = None


def upgrade():
    # message user table: create table
    op.create_table('message_user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('full_name', sa.String(length=128), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('_role', sa.String(length=15), nullable=True),
    sa.Column('read', mysql.TINYINT(display_width=1), nullable=True),
    sa.Column('tag', sa.String(length=20), nullable=True),
    sa.Column('message_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(
        ['message_id'], ['message.id'],
        name=op.f('fk_message_user_message_id_message'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(
        ['user_id'], ['user.id'], name=op.f('fk_message_user_user_id_user')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_message_user'))
    ),
    op.create_index(
        op.f('ix_message_user_read'), 'message_user', ['read'],
        unique=False)
    op.create_index(
        op.f('ix_message_user_tag'), 'message_user', ['tag'],
        unique=False)

    # user table: add column
    op.add_column(
        'user', sa.Column('role', sa.String(length=12), nullable=True)
    )

    # recipient data table: drop
    op.drop_index(op.f('ix_recipient_data_read'), table_name='recipient_data')
    op.drop_index(op.f('ix_recipient_data_status'), table_name='recipient_data')
    op.drop_table('recipient_data')

    # message table: remove columns/indexs/constraints
    op.drop_index(op.f('ix_message_read'), table_name='message')
    op.drop_index(op.f('ix_message_status'), table_name='message')
    op.drop_constraint(
        'fk_message_sender_id_user', 'message', type_='foreignkey'
    )   
    op.drop_column('message', 'read')
    op.drop_column('message', 'status')
    op.drop_column('message', 'sender_id')


def downgrade():
    # recipient table : create table
    op.create_table('recipient_data',
    sa.Column(
        'id', mysql.INTEGER(display_width=11), autoincrement=True,
        nullable=False
    ),
    sa.Column(
        'user_id', mysql.INTEGER(display_width=11), autoincrement=False,
        nullable=False
    ),
    sa.Column(
        'message_id', mysql.INTEGER(display_width=11), autoincrement=False,
        nullable=False
    ),
    sa.Column(
        'read', mysql.TINYINT(display_width=1), autoincrement=False,
        nullable=True, default=None
    ),
    sa.Column(
        'status', mysql.VARCHAR(collation='utf8_bin', length=20),
        nullable=True, default=None
    ),
    sa.ForeignKeyConstraint(
        ['message_id'], ['message.id'],
        name='fk_recipient_data_message_id_message', ondelete='CASCADE'
    ),
    sa.ForeignKeyConstraint(
        ['user_id'], ['user.id'],
        name='fk_recipient_data_user_id_user'
    ),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8_bin',
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.create_index(
        'ix_recipient_data_read', 'recipient_data', ['read'],
        unique=False
    )
    op.create_index(
        'ix_recipient_data_status', 'recipient_data', ['status'],
        unique=False
    )

    # message user table: drop table
    op.drop_index(op.f('ix_message_user_tag'), table_name='message_user')
    op.drop_index(op.f('ix_message_user_read'), table_name='message_user')
    op.drop_table('message_user')

    # user: drop column
    op.drop_column('user', 'role')

    # message: add columns
    op.add_column('message', sa.Column('read', mysql.TINYINT(display_width=1), nullable=True))
    op.add_column('message', sa.Column('status', sa.String(20), nullable=True))
    op.add_column(
        'message', sa.Column('sender_id',  mysql.INTEGER(display_width=11), nullable=True)
    )
    op.create_index('ix_message_read', 'message', ['read'], unique=False)
    op.create_index('ix_message_status', 'message', ['status'], unique=False)
    op.create_foreign_key(
        'fk_message_sender_id_user', 'message', 'user', ['sender_id'], ['id']
    )
