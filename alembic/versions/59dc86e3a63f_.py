"""empty message

Revision ID: 59dc86e3a63f
Revises: 
Create Date: 2022-12-15 17:22:52.777533

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '59dc86e3a63f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('hashed_password', sa.Text(), nullable=True),
    sa.Column('username', sa.String(length=50), nullable=False),
    sa.Column('activated', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('user_id'),
    sa.UniqueConstraint('hashed_password')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_user_id'), 'users', ['user_id'], unique=False)
    op.create_table('codes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('reset_code', sa.String(length=50), nullable=True),
    sa.Column('verify_code', sa.String(length=50), nullable=True),
    sa.Column('expires_reset_code', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_codes_id'), 'codes', ['id'], unique=False)
    op.create_table('profiles',
    sa.Column('profile_id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=50), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('profile_id')
    )
    op.create_index(op.f('ix_profiles_profile_id'), 'profiles', ['profile_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_profiles_profile_id'), table_name='profiles')
    op.drop_table('profiles')
    op.drop_index(op.f('ix_codes_id'), table_name='codes')
    op.drop_table('codes')
    op.drop_index(op.f('ix_users_user_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###