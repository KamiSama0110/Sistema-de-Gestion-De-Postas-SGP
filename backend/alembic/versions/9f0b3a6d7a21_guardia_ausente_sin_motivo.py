"""permite ausente sin motivo

Revision ID: 9f0b3a6d7a21
Revises: 7688404045a5
Create Date: 2026-05-25 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "9f0b3a6d7a21"
down_revision: Union[str, Sequence[str], None] = "7688404045a5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TABLE guardia DROP CONSTRAINT IF EXISTS ck_guardia_ausencia_motivo")


def downgrade() -> None:
    """Downgrade schema."""
    op.create_check_constraint(
        "ck_guardia_ausencia_motivo",
        "guardia",
        "estado != 'ausente' OR motivo_ausencia IS NOT NULL",
    )
