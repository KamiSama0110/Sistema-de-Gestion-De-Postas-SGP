"""usuario rol cuadro check

Revision ID: 9dd8b6ba266f
Revises: 19c4fd86af89
Create Date: 2026-11-03 00:12:08.621189

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9dd8b6ba266f'
down_revision: Union[str, Sequence[str], None] = '19c4fd86af89'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM usuario
                WHERE (rol = 'cuadro' AND cuadro_id IS NULL)
                   OR (rol = 'admin' AND cuadro_id IS NOT NULL)
            ) THEN
                RAISE EXCEPTION
                    'Existen usuarios con rol y cuadro_id incoherentes; corrígelos antes de aplicar esta migración';
            END IF;
        END $$;
        """
    )
    op.create_check_constraint(
        "ck_usuario_rol_cuadro",
        "usuario",
        "(rol = 'cuadro' AND cuadro_id IS NOT NULL) "
        "OR (rol = 'admin' AND cuadro_id IS NULL)",
    )


def downgrade() -> None:
    op.drop_constraint("ck_usuario_rol_cuadro", "usuario", type_="check")
