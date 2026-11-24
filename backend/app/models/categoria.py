from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..core.database import Base

if TYPE_CHECKING:
    from .libro import Libro


class Categoria(Base):
    """Modelo ORM para la tabla categorias."""
    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    descripcion: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # Relación muchos a muchos con Libro a través de libro_categoria
    libros: Mapped[list["Libro"]] = relationship(
        "Libro",
        secondary="libro_categoria",
        back_populates="categorias"
    )
