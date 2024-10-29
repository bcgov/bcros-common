"""0005_document_author

Revision ID: e26474330753
Revises: d41256aa4367
Create Date: 2024-10-29 03:11:16.811753

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e26474330753'
down_revision = 'd41256aa4367'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('documents', schema=None) as batch_op:
        batch_op.add_column(sa.Column('author', sa.String(length=256), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('documents', schema=None) as batch_op:
        batch_op.drop_column('author')

    # ### end Alembic commands ###
