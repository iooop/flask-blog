"""empty message

Revision ID: a511a1814adf
Revises: None
Create Date: 2016-04-08 01:24:18.859942

"""

# revision identifiers, used by Alembic.
revision = 'a511a1814adf'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('entry', sa.Column('status', sa.SmallInteger(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('entry', 'status')
    ### end Alembic commands ###
