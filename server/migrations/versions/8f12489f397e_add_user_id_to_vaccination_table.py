"""Add user_id to Vaccination table

Revision ID: 8f12489f397e
Revises: 2e2c9e53554c
Create Date: 2024-11-18 22:14:06.849312

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8f12489f397e'
down_revision = '2e2c9e53554c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'appointment', 'user', ['user_id'], ['id'])
    op.add_column('vaccination', sa.Column('user_id', sa.String(length=36), nullable=False))
    op.create_foreign_key(None, 'vaccination', 'user', ['user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'vaccination', type_='foreignkey')
    op.drop_column('vaccination', 'user_id')
    op.drop_constraint(None, 'appointment', type_='foreignkey')
    # ### end Alembic commands ###
