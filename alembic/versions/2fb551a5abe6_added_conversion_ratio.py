"""added_conversion_ratio

Revision ID: 2fb551a5abe6
Revises: 0ac0e12b0cdb
Create Date: 2024-07-18 18:25:03.465271

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2fb551a5abe6'
down_revision = '0ac0e12b0cdb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('token_pair', sa.Column('conversion_ratio', sa.DECIMAL(precision=32, scale=18), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('token_pair', 'conversion_ratio')
    # ### end Alembic commands ###
