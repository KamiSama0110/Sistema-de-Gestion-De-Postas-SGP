"""insertar franjas iniciales

Revision ID: 32c2a4d43602
Revises: a4176a62d05e
Create Date: 2026-10-19 04:04:50.822858

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "32c2a4d43602"
down_revision: str | Sequence[str] | None = "a4176a62d05e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
           INSERT INTO franja_cuadro (nombre, hora_inicio, hora_fin, dias_semana, sexo_permitido, activa)
           VALUES
               ('diurna',   '09:00', '16:00', ARRAY[5, 6],                 'femenino',  true),
               ('nocturna', '17:00', '07:00', ARRAY[0, 1, 2, 3, 4, 5, 6],  'masculino', true)
           ON CONFLICT (nombre) DO NOTHING
           """
    )


def downgrade() -> None:
    pass
