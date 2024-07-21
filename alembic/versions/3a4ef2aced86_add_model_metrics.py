"""add model_metrics

Revision ID: 3a4ef2aced86
Revises: 
Create Date: 2024-07-21 21:36:05.078831

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '3a4ef2aced86'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'model_metrics',
        sa.Column('id', sa.UUID, primary_key=True),
        sa.Column('model_key', sa.UUID, nullable=False),
        sa.Column('ticker_symbol', sa.String(5), nullable=False),
        sa.Column('interval', sa.String(3), nullable=False),
        sa.Column('mse', sa.Float, nullable=False),
        sa.Column('mae', sa.Float, nullable=False),
        sa.Column('r2', sa.Float, nullable=False),
        sa.Column('timestamp', sa.DateTime, server_default=sa.func.now(), nullable=False)
    )


def downgrade() -> None:
    pass
