"""Initial schema

Revision ID: 25276717e6b8
Revises: None
Create Date: 2016-03-25 17:58:19.963883

"""

# revision identifiers, used by Alembic.
revision = '25276717e6b8'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_table('server_log')
    op.drop_table('user')
    op.drop_table('server')
    op.drop_table('user_on_server')


def downgrade():
    op.create_table('user_on_server',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.TEXT(), nullable=True),
    sa.Column('auto_pub_threshold', sa.INTEGER(), nullable=True),
    sa.Column('server_id', sa.INTEGER(), nullable=True),
    sa.Column('user_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['server_id'], ['server.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('server',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.TEXT(), nullable=True),
    sa.Column('log_uri_template', sa.TEXT(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('uri', sa.TEXT(), nullable=True),
    sa.Column('micropub_uri', sa.TEXT(), nullable=True),
    sa.Column('access_token', sa.TEXT(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('server_log',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('uri', sa.TEXT(), nullable=True),
    sa.Column('position', sa.INTEGER(), nullable=True),
    sa.Column('server_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['server_id'], ['server.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
