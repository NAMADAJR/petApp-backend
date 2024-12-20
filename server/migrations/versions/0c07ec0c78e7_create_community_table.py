"""Create Community table

Revision ID: 0c07ec0c78e7
Revises: fd6673800949
Create Date: 2024-11-21 22:15:08.385308

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0c07ec0c78e7'
down_revision = 'fd6673800949'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('community',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('comment', sa.Text(), nullable=True),
    sa.Column('picture', sa.String(length=255), nullable=True),
    sa.Column('gif', sa.String(length=255), nullable=True),
    sa.Column('emoji', sa.String(length=50), nullable=True),
    sa.Column('likes', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_foreign_key(None, 'appointment', 'user', ['user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'appointment', type_='foreignkey')
    op.drop_table('community')
    # ### end Alembic commands ###
