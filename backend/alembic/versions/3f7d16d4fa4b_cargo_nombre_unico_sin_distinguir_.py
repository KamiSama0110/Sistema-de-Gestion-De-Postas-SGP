"""cargo nombre unico sin distinguir mayusculas

Revision ID: 3f7d16d4fa4b
Revises: e4be5fe00ad1
Create Date: 2026-11-04 17:46:43.789015

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3f7d16d4fa4b'
down_revision: Union[str, Sequence[str], None] = 'e4be5fe00ad1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    duplicados = op.get_bind().execute(
        sa.text(
            "SELECT lower(nombre) AS nombre, count(*) AS cantidad "
            "FROM cargo GROUP BY 1 HAVING count(*) > 1"
        )
    ).all()
    if duplicados:
        detalle = ", ".join(f"'{fila.nombre}' ({fila.cantidad})" for fila in duplicados)
        raise RuntimeError(
            "No se puede crear el índice único de cargos: hay nombres "
            f"repetidos sin distinguir mayúsculas: {detalle}. "
            "Resuélvelos antes de aplicar esta migración."
        )

    op.create_index(
        "ix_cargo_nombre_lower",
        "cargo",
        [sa.text("lower(nombre)")],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_cargo_nombre_lower", table_name="cargo")
