from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import Boolean, Date, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..core.database import Base

if TYPE_CHECKING:
    from .libro import Libro
    from .socio import Socio
    from .usuario import Usuario


class Prestamo(Base):
    """Modelo ORM para la tabla prestamos."""
    __tablename__ = "prestamos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    libro_id: Mapped[int] = mapped_column(ForeignKey("libros.id"), nullable=False)
    socio_id: Mapped[int] = mapped_column(ForeignKey("socios.id"), nullable=False)
    fecha_prestamo: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)
    fecha_limite: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_devolucion: Mapped[date | None] = mapped_column(Date, nullable=True)
    multa: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal("0.00"),
        nullable=False
    )
    multa_pagada: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    registrado_por_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True
    )

    # Relaciones
    libro: Mapped["Libro"] = relationship("Libro", back_populates="prestamos")
    socio: Mapped["Socio"] = relationship("Socio", back_populates="prestamos")
    registrado_por: Mapped["Usuario | None"] = relationship(
        "Usuario",
        back_populates="prestamos_registrados"
    )
