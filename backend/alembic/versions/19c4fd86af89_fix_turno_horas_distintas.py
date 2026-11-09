"""fix turno horas distintas

Revision ID: 19c4fd86af89
Revises: 32c2a4d43602
Create Date: 2026-11-03 00:12:08.217602

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '19c4fd86af89'
down_revision: Union[str, Sequence[str], None] = '32c2a4d43602'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE turno_posta
        SET hora_fin = (hora_inicio + interval '1 hour')::time,
            cruza_medianoche = ((hora_inicio + interval '1 hour')::time < hora_inicio)
        WHERE hora_inicio = hora_fin
        """
    )
    op.create_check_constraint(
        "ck_turno_horas_distintas",
        "turno_posta",
        "hora_inicio <> hora_fin",
    )


def downgrade() -> None:
    op.drop_constraint("ck_turno_horas_distintas", "turno_posta", type_="check")
