from typing import TYPE_CHECKING
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..core.database import Base

if TYPE_CHECKING:
    from .libro import Libro


class Autor(Base):
    """Modelo ORM para la tabla autores."""
    __tablename__ = "autores"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    nacionalidad: Mapped[str | None] = mapped_column(String(60), nullable=True)
    anio_nacimiento: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Relación uno a muchos con Libro
    libros: Mapped[list["Libro"]] = relationship("Libro", back_populates="autor")
