from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING
from sqlalchemy import Boolean, DateTime, Enum as SQLEnum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..core.database import Base

if TYPE_CHECKING:
    from .socio import Socio
    from .refresh_token import RefreshToken
    from .prestamo import Prestamo


class RolUsuario(str, Enum):
    admin = "admin"
    bibliotecario = "bibliotecario"
    socio = "socio"


class Usuario(Base):
    """Modelo ORM para la tabla usuarios."""
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    rol: Mapped[RolUsuario] = mapped_column(
        SQLEnum(RolUsuario, name="rolusuario"),
        default=RolUsuario.socio,
        nullable=False
    )
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    intentos_fallidos: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    bloqueado_hasta: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    socio_id: Mapped[int | None] = mapped_column(ForeignKey("socios.id"), unique=True, nullable=True)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relaciones
    socio: Mapped["Socio | None"] = relationship("Socio", back_populates="usuario")
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken",
        back_populates="usuario",
        cascade="all, delete-orphan"
    )
    prestamos_registrados: Mapped[list["Prestamo"]] = relationship(
        "Prestamo",
        back_populates="registrado_por"
    )

