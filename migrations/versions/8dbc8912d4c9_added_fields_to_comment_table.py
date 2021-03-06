"""Added fields to comment table

Revision ID: 8dbc8912d4c9
Revises: 41ff37010861
Create Date: 2018-12-30 18:16:52.255140

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8dbc8912d4c9'
down_revision = '41ff37010861'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('comment', sa.Column('date', sa.DateTime(), nullable=True))
    op.add_column('comment', sa.Column('upvotes', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_comment_date'), 'comment', ['date'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_comment_date'), table_name='comment')
    op.drop_column('comment', 'upvotes')
    op.drop_column('comment', 'date')
    # ### end Alembic commands ###
