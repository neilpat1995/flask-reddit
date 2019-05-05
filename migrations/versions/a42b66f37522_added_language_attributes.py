"""Added language attributes

Revision ID: a42b66f37522
Revises: 8dbc8912d4c9
Create Date: 2019-04-14 02:25:42.675191

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a42b66f37522'
down_revision = '8dbc8912d4c9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('comment', sa.Column('language', sa.String(length=5), nullable=True))
    op.add_column('subreddit', sa.Column('language', sa.String(length=5), nullable=True))
    op.add_column('thread', sa.Column('language', sa.String(length=5), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('thread', 'language')
    op.drop_column('subreddit', 'language')
    op.drop_column('comment', 'language')
    # ### end Alembic commands ###
