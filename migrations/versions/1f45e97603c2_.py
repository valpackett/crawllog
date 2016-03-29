"""empty message

Revision ID: 1f45e97603c2
Revises: 25276717e6b8
Create Date: 2016-03-29 23:31:09.703927

"""

# revision identifiers, used by Alembic.
revision = '1f45e97603c2'
down_revision = '25276717e6b8'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('server_log', sa.Column('crawl_month_fix', sa.Boolean(), nullable=True))
    op.add_column('server_log', sa.Column('uri_template', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('server_log', 'uri_template')
    op.drop_column('server_log', 'crawl_month_fix')
