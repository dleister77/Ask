"""update provider website length

Revision ID: 16d606638454
Revises: b37ce618f530
Create Date: 2020-02-27 15:40:47.231583

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '16d606638454'
down_revision = 'b37ce618f530'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('provider',
                     'website',
                     existing_type=sa.String(30),
                     type_=sa.String(120),
                     nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('provider',
                    'website',
                     existing_type=sa.String(120),
                     type_=sa.String(30),
                     nullable=True)
    # ### end Alembic commands ###