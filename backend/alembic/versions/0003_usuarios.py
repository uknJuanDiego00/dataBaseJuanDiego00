# -*- coding: utf-8 -*-
"""0003 usuarios - tabla de usuarios con roles y relación socio

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-27 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Enum de roles
rolusuario_enum = postgresql.ENUM(
    "admin", "bibliotecario", "socio",
    name="rolusuario",
    create_type=False
)


def upgrade() -> None:
    # Crear el tipo ENUM en PostgreSQL
    rolusuario_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("email", sa.String(150), nullable=False),
        sa.Column("nombre", sa.String(100), nullable=False),
        sa.Column("password_hash", sa.String(256), nullable=False),
        sa.Column(
            "rol",
            sa.Enum("admin", "bibliotecario", "socio", name="rolusuario"),
            nullable=False,
            server_default="socio"
        ),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("intentos_fallidos", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("bloqueado_hasta", sa.DateTime(timezone=True), nullable=True),
        sa.Column("socio_id", sa.Integer(), nullable=True),
        sa.Column(
            "creado_en",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()")
        ),
        sa.ForeignKeyConstraint(
            ["socio_id"], ["socios.id"],
            name=op.f("fk_usuarios_socio_id_socios")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_usuarios")),
        sa.UniqueConstraint("email", name=op.f("uq_usuarios_email")),
        sa.UniqueConstraint("socio_id", name=op.f("uq_usuarios_socio_id")),
    )
    op.create_index(op.f("ix_usuarios_email"), "usuarios", ["email"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_usuarios_email"), table_name="usuarios")
    op.drop_table("usuarios")
    # Eliminar el tipo ENUM de PostgreSQL
    rolusuario_enum.drop(op.get_bind(), checkfirst=True)

