"""scrub audit sensitive fields

Revision ID: e4be5fe00ad1
Revises: 9dd8b6ba266f
Create Date: 2026-11-03 00:12:08.983393

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e4be5fe00ad1'
down_revision: Union[str, Sequence[str], None] = '9dd8b6ba266f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE audit_log
        SET datos_anteriores = (
            datos_anteriores::jsonb - 'hashed_password' - 'token_hash'
        )::text
        WHERE datos_anteriores IS NOT NULL
          AND (
              jsonb_exists(datos_anteriores::jsonb, 'hashed_password')
              OR jsonb_exists(datos_anteriores::jsonb, 'token_hash')
          )
        """
    )
    op.execute(
        """
        UPDATE audit_log
        SET datos_nuevos = (
            datos_nuevos::jsonb - 'hashed_password' - 'token_hash'
        )::text
        WHERE datos_nuevos IS NOT NULL
          AND (
              jsonb_exists(datos_nuevos::jsonb, 'hashed_password')
              OR jsonb_exists(datos_nuevos::jsonb, 'token_hash')
          )
        """
    )


def downgrade() -> None:
    pass
