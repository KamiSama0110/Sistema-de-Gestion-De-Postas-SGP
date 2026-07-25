"""add indexes + fix posta_creado_en type

Revision ID: 5e78d32b1624
Revises: 9f0b3a6d7a21
Create Date: 2026-07-18 18:02:09.056804

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '5e78d32b1624'
down_revision: Union[str, Sequence[str], None] = '9f0b3a6d7a21'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE INDEX IF NOT EXISTS ix_guardia_fecha_estado ON guardia (fecha, estado)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_guardia_turno_posta_id ON guardia (turno_posta_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_novedad_guardia_id ON novedad (guardia_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_turno_posta_posta_id ON turno_posta (posta_id)")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP INDEX IF EXISTS ix_turno_posta_posta_id")
    op.execute("DROP INDEX IF EXISTS ix_novedad_guardia_id")
    op.execute("DROP INDEX IF EXISTS ix_guardia_turno_posta_id")
    op.execute("DROP INDEX IF EXISTS ix_guardia_fecha_estado")
