"""Make description not nullable and unique

Revision ID: 17fd243e4dc4
Revises: 550127b0c073
Create Date: 2017-09-19 10:49:50.261083

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '17fd243e4dc4'
down_revision = '5f6302b63190'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('event', 'description',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.create_unique_constraint(None, 'event', ['description'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'event', type_='unique')
    op.alter_column('event', 'description',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###