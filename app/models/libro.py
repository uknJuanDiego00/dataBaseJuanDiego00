from typing import TYPE_CHECKING
from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..core.database import Base

if TYPE_CHECKING:
    from .autor import Autor
    from .categoria import Categoria
    from .prestamo import Prestamo

# Tabla intermedia para la relación muchos a muchos entre Libros y Categorías
libro_categoria = Table(
    "libro_categoria",
    Base.metadata,
    Column(
        "libro_id",
        Integer,
        ForeignKey("libros.id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "categoria_id",
        Integer,
        ForeignKey("categorias.id", ondelete="CASCADE"),
        primary_key=True
    )
)


class Libro(Base):
    """Modelo ORM para la tabla libros."""
    __tablename__ = "libros"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    titulo: Mapped[str] = mapped_column(String(150), nullable=False)
    isbn: Mapped[str] = mapped_column(String(13), unique=True, nullable=False, index=True)
    anio_publicacion: Mapped[int] = mapped_column(Integer, nullable=False)
    ejemplares: Mapped[int] = mapped_column(Integer, nullable=False)
    autor_id: Mapped[int] = mapped_column(ForeignKey("autores.id"), nullable=False)

    # Relaciones
    autor: Mapped["Autor"] = relationship("Autor", back_populates="libros")
    categorias: Mapped[list["Categoria"]] = relationship(
        "Categoria",
        secondary=libro_categoria,
        back_populates="libros"
    )
    prestamos: Mapped[list["Prestamo"]] = relationship(
        "Prestamo",
        back_populates="libro"
    )
