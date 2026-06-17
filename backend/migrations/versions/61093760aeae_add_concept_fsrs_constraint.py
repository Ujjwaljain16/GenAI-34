"""add concept fsrs constraint

Revision ID: 61093760aeae
Revises: 5b1e5073d1f6
Create Date: 2026-06-18 01:57:08.206577

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '61093760aeae'
down_revision: Union[str, Sequence[str], None] = '5b1e5073d1f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint('uq_user_concept_fsrs', 'concept_fsrs', ['user_id', 'concept_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('uq_user_concept_fsrs', 'concept_fsrs', type_='unique')
