"""empty message

Revision ID: f0bcbe3ecadb
Revises: 842c39c04d89
Create Date: 2019-07-03 23:48:56.056654

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f0bcbe3ecadb'
down_revision = '842c39c04d89'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('subreddit', sa.Column('description', sa.String(length=256), nullable=True))
    op.create_unique_constraint(None, 'subreddit', ['description'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'subreddit', type_='unique')
    op.drop_column('subreddit', 'description')
    # ### end Alembic commands ###
