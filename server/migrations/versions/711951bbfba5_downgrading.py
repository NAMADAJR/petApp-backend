"""downgrading

Revision ID: 711951bbfba5
Revises: 3550de5a408a
Create Date: 2024-11-26 09:17:22.448291

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '711951bbfba5'
down_revision = '3550de5a408a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('appointment', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'user', ['user_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('appointment', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')

    # ### end Alembic commands ###
