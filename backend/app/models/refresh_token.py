from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..core.database import Base

if TYPE_CHECKING:
    from .usuario import Usuario


class RefreshToken(Base):
    """Modelo ORM para la tabla refresh_tokens."""
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    jti: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, index=True)
    usuario_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False
    )
    expira_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revocado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relación con Usuario
    usuario: Mapped["Usuario"] = relationship("Usuario", back_populates="refresh_tokens")

