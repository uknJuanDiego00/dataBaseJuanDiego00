# -*- coding: utf-8 -*-
"""0002 multa pagada - agregar columna multa_pagada a prestamos

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-27 09:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Agregar columna multa_pagada con server_default false
    op.add_column(
        "prestamos",
        sa.Column(
            "multa_pagada",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false")
        )
    )
    # Migración de datos: marcar como pagada si multa == 0
    op.execute(
        "UPDATE prestamos SET multa_pagada = TRUE WHERE multa = 0"
    )


def downgrade() -> None:
    op.drop_column("prestamos", "multa_pagada")

