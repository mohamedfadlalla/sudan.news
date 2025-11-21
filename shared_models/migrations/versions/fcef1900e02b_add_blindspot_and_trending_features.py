"""Add blindspot and trending features

Revision ID: fcef1900e02b
Revises: 8fa321b4b617
Create Date: 2025-11-20 01:58:39.692246

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fcef1900e02b'
down_revision: Union[str, Sequence[str], None] = '8fa321b4b617'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - add blindspot and trending columns to clusters table."""
    # Blindspot detection columns
    op.add_column('clusters', sa.Column('blindspot_type', sa.String(), nullable=True))
    op.add_column('clusters', sa.Column('bias_coverage_pro', sa.Integer(), server_default='0', nullable=False))
    op.add_column('clusters', sa.Column('bias_coverage_neutral', sa.Integer(), server_default='0', nullable=False))
    op.add_column('clusters', sa.Column('bias_coverage_oppose', sa.Integer(), server_default='0', nullable=False))
    op.add_column('clusters', sa.Column('bias_balance_score', sa.Float(), server_default='0.0', nullable=False))
    
    # Trending topics columns
    op.add_column('clusters', sa.Column('coverage_velocity', sa.Float(), server_default='0.0', nullable=False))
    op.add_column('clusters', sa.Column('is_trending', sa.Boolean(), server_default='0', nullable=False))
    op.add_column('clusters', sa.Column('first_seen_at', sa.String(), nullable=True))
    op.add_column('clusters', sa.Column('last_coverage_check', sa.String(), nullable=True))
    op.add_column('clusters', sa.Column('coverage_history', sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema - remove blindspot and trending columns."""
    # Remove blindspot columns
    op.drop_column('clusters', 'blindspot_type')
    op.drop_column('clusters', 'bias_coverage_pro')
    op.drop_column('clusters', 'bias_coverage_neutral')
    op.drop_column('clusters', 'bias_coverage_oppose')
    op.drop_column('clusters', 'bias_balance_score')
    
    # Remove trending columns
    op.drop_column('clusters', 'coverage_velocity')
    op.drop_column('clusters', 'is_trending')
    op.drop_column('clusters', 'first_seen_at')
    op.drop_column('clusters', 'last_coverage_check')
    op.drop_column('clusters', 'coverage_history')
