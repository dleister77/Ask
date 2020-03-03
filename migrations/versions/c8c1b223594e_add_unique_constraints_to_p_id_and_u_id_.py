"""add unique constraints to p_id and u_id in address

Revision ID: c8c1b223594e
Revises: 16d606638454
Create Date: 2020-02-28 09:25:31.512720

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c8c1b223594e'
down_revision = '16d606638454'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(op.f('uq_address_provider_id'), 'address', ['provider_id'])
    op.create_unique_constraint(op.f('uq_address_user_id'), 'address', ['user_id'])
    op.create_unique_constraint('unique_cat_prov', 'category_provider', ['category_id', 'provider_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('unique_cat_prov', 'category_provider', type_='unique')
    op.drop_constraint(op.f('uq_address_user_id'), 'address', type_='unique')
    op.drop_constraint(op.f('uq_address_provider_id'), 'address', type_='unique')
    # ### end Alembic commands ###
