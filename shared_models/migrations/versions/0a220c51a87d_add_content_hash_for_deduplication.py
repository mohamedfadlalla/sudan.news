"""add_content_hash_for_deduplication

Revision ID: 0a220c51a87d
Revises: fcef1900e02b
Create Date: 2025-11-25 09:20:26.820869

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0a220c51a87d'
down_revision: Union[str, Sequence[str], None] = 'fcef1900e02b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - add content_hash column for article deduplication."""
    # For SQLite, we need to use batch mode to add constraints
    with op.batch_alter_table('articles') as batch_op:
        # Add content_hash column as nullable initially
        batch_op.add_column(sa.Column('content_hash', sa.String(), nullable=True))

        # Add unique constraint on content_hash
        batch_op.create_unique_constraint('uq_articles_content_hash', ['content_hash'])


def downgrade() -> None:
    """Downgrade schema - remove content_hash column."""
    # Remove unique constraint first
    op.drop_constraint('uq_articles_content_hash', 'articles', type_='unique')

    # Remove the column
    op.drop_column('articles', 'content_hash')
