from sqlalchemy import func, select
from sqlalchemy.orm import Session
from ..core.exceptions import Conflicto, NoEncontrado
from ..models.categoria import Categoria
from ..models.libro import libro_categoria
from ..schemas.categoria import CategoriaActualizar, CategoriaCrear


def listar_categorias(
    db: Session,
    skip: int = 0,
    limit: int = 10
) -> list[Categoria]:
    """Retorna una lista paginada de categorías."""
    consulta = select(Categoria).order_by(Categoria.id).offset(skip).limit(limit)
    return list(db.scalars(consulta).all())


def obtener_categoria(db: Session, categoria_id: int) -> Categoria:
    """Retorna una categoría por su ID o lanza NoEncontrado si no existe."""
    categoria = db.get(Categoria, categoria_id)
    if not categoria:
        raise NoEncontrado("Categoría no encontrada")
    return categoria


def crear_categoria(db: Session, datos: CategoriaCrear) -> Categoria:
    """Crea una nueva categoría validando unicidad de nombre en minúsculas."""
    existente = db.scalar(
        select(Categoria).where(Categoria.nombre == datos.nombre)
    )
    if existente:
        raise Conflicto("Ya existe una categoría con ese nombre")

    nueva_categoria = Categoria(
        nombre=datos.nombre,
        descripcion=datos.descripcion
    )
    db.add(nueva_categoria)
    db.commit()
    db.refresh(nueva_categoria)
    return nueva_categoria


def actualizar_categoria(
    db: Session,
    categoria_id: int,
    datos: CategoriaActualizar
) -> Categoria:
    """Actualiza una categoría validando unicidad si cambia el nombre."""
    categoria = obtener_categoria(db, categoria_id)

    if datos.nombre is not None:
        existente = db.scalar(
            select(Categoria).where(
                Categoria.nombre == datos.nombre,
                Categoria.id != categoria_id
            )
        )
        if existente:
            raise Conflicto("Ya existe otra categoría con ese nombre")
        categoria.nombre = datos.nombre

    if datos.descripcion is not None:
        categoria.descripcion = datos.descripcion

    db.commit()
    db.refresh(categoria)
    return categoria


def eliminar_categoria(db: Session, categoria_id: int) -> None:
    """Elimina una categoría quitándola de los libros que la tenían."""
    categoria = obtener_categoria(db, categoria_id)

    # Eliminar las relaciones asociadas en la tabla intermedia libro_categoria
    db.execute(
        libro_categoria.delete().where(libro_categoria.c.categoria_id == categoria_id)
    )
    db.delete(categoria)
    db.commit()
