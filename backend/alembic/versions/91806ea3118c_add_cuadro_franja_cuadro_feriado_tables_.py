"""add cuadro, franja_cuadro, feriado tables and usuario.cuadro_id fk

Revision ID: 91806ea3118c
Revises: d178b3153cb9
Create Date: 2026-10-11 13:53:43.904186
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '91806ea3118c'
down_revision: Union[str, Sequence[str], None] = 'd178b3153cb9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # cuadro
    op.create_table('cuadro',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.String(length=100), nullable=False),
        sa.Column('apellidos', sa.String(length=150), nullable=False),
        sa.Column('ci', sa.String(length=20), nullable=True),
        sa.Column('cargo', sa.String(length=100), nullable=False),
        sa.Column('area', sa.String(length=100), nullable=False),
        sa.Column('telefono', sa.String(length=20), nullable=True),
        sa.Column('sexo', sa.Enum('masculino', 'femenino', name='sexoenum'), nullable=False),
        sa.Column('activo', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('sin_guardia_vie_dom', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('observaciones', sa.Text(), nullable=True),
        sa.Column('creado_en', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('ci')
    )

    # franja_cuadro
    op.create_table('franja_cuadro',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.String(length=50), nullable=False),
        sa.Column('hora_inicio', sa.String(length=5), nullable=False),
        sa.Column('hora_fin', sa.String(length=5), nullable=False),
        sa.Column('dias_semana', sa.ARRAY(sa.Integer()), nullable=False),
        sa.Column('sexo_permitido', sa.Enum('masculino', 'femenino', name='sexoenum'), nullable=False),
        sa.Column('activa', sa.Boolean(), server_default='true', nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('nombre')
    )

    # feriado
    op.create_table('feriado',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('fecha', sa.DateTime(), nullable=False),
        sa.Column('descripcion', sa.String(length=200), nullable=False),
        sa.Column('creado_en', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('fecha')
    )

    # FK usuario.cuadro_id -> cuadro.id (unique)
    op.create_foreign_key(
        'usuario_cuadro_id_fkey',
        'usuario',
        'cuadro',
        ['cuadro_id'],
        ['id']
    )
    op.create_unique_constraint(
        'usuario_cuadro_id_key',
        'usuario',
        ['cuadro_id']
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('usuario_cuadro_id_key', 'usuario', type_='unique')
    op.drop_constraint('usuario_cuadro_id_fkey', 'usuario', type_='foreignkey')
    op.drop_table('feriado')
    op.drop_table('franja_cuadro')
    op.drop_table('cuadro')
