"""add timestamp to provider_suggestion

Revision ID: 430241867918
Revises: fc8082fd60a6
Create Date: 2020-04-27 14:08:01.893695

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '430241867918'
down_revision = 'fc8082fd60a6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('provider_suggestion', sa.Column('timestamp', sa.DateTime(), nullable=True))
    op.create_index(op.f('ix_provider_suggestion_timestamp'), 'provider_suggestion', ['timestamp'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_provider_suggestion_timestamp'), table_name='provider_suggestion')
    op.drop_column('provider_suggestion', 'timestamp')
    # ### end Alembic commands ###
