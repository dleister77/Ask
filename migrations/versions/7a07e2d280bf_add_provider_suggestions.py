"""add provider suggestions

Revision ID: 7a07e2d280bf
Revises: 10edb68acf2c
Create Date: 2020-03-10 19:15:30.018444

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7a07e2d280bf'
down_revision = '10edb68acf2c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('provider_suggestion',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('provider_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('telephone', sa.String(length=24), nullable=True),
    sa.Column('website', sa.String(length=120), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('other', sa.String(length=1000), nullable=True),
    sa.ForeignKeyConstraint(['provider_id'], ['provider.id'], name=op.f('fk_provider_suggestion_provider_id_provider'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name=op.f('fk_provider_suggestion_user_id_user'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_provider_suggestion'))
    )
    op.create_index(op.f('ix_provider_suggestion_is_active'), 'provider_suggestion', ['is_active'], unique=False)
    op.create_index(op.f('ix_provider_suggestion_name'), 'provider_suggestion', ['name'], unique=False)
    op.create_table('address_suggestion',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('line1', sa.String(length=128), nullable=True),
    sa.Column('line2', sa.String(length=128), nullable=True),
    sa.Column('zip', sa.String(length=20), nullable=True),
    sa.Column('city', sa.String(length=64), nullable=False),
    sa.Column('provider_suggestion_id', sa.Integer(), nullable=True),
    sa.Column('state_id', sa.Integer(), nullable=False),
    sa.Column('is_coordinate_error', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['provider_suggestion_id'], ['provider_suggestion.id'], name=op.f('fk_address_suggestion_provider_suggestion_id_provider_suggestion'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['state_id'], ['state.id'], name=op.f('fk_address_suggestion_state_id_state')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_address_suggestion')),
    sa.UniqueConstraint('provider_suggestion_id', name=op.f('uq_address_suggestion_provider_suggestion_id'))
    )
    op.create_index(op.f('ix_address_suggestion_city'), 'address_suggestion', ['city'], unique=False)
    op.create_index(op.f('ix_address_suggestion_is_coordinate_error'), 'address_suggestion', ['is_coordinate_error'], unique=False)
    op.create_index(op.f('ix_address_suggestion_zip'), 'address_suggestion', ['zip'], unique=False)
    op.create_table('cat_prov_suggest',
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.Column('provider_suggestion_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['category.id'], name=op.f('fk_cat_prov_suggest_category_id_category')),
    sa.ForeignKeyConstraint(['provider_suggestion_id'], ['provider_suggestion.id'], name=op.f('fk_cat_prov_suggest_provider_suggestion_id_provider_suggestion'), ondelete='CASCADE')
    )
    op.add_column('provider', sa.Column('is_active', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('provider', 'is_active')
    op.drop_table('cat_prov_suggest')
    op.drop_index(op.f('ix_address_suggestion_zip'), table_name='address_suggestion')
    op.drop_index(op.f('ix_address_suggestion_is_coordinate_error'), table_name='address_suggestion')
    op.drop_index(op.f('ix_address_suggestion_city'), table_name='address_suggestion')
    op.drop_table('address_suggestion')
    op.drop_index(op.f('ix_provider_suggestion_name'), table_name='provider_suggestion')
    op.drop_index(op.f('ix_provider_suggestion_is_active'), table_name='provider_suggestion')
    op.drop_table('provider_suggestion')
    # ### end Alembic commands ###