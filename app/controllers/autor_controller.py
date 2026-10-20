from sqlalchemy import func, select
from sqlalchemy.orm import Session
from ..core.exceptions import Conflicto, NoEncontrado
from ..models.autor import Autor
from ..models.libro import Libro
from ..schemas.autor import AutorActualizar, AutorCrear


def listar_autores(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    nacionalidad: str | None = None
) -> list[Autor]:
    """Retorna una lista paginada de autores con filtro opcional por nacionalidad."""
    consulta = select(Autor)
    if nacionalidad:
        consulta = consulta.where(Autor.nacionalidad.ilike(f"%{nacionalidad.strip()}%"))
    consulta = consulta.order_by(Autor.id).offset(skip).limit(limit)
    return list(db.scalars(consulta).all())


def obtener_autor(db: Session, autor_id: int) -> Autor:
    """Retorna un autor por su ID o lanza NoEncontrado si no existe."""
    autor = db.get(Autor, autor_id)
    if not autor:
        raise NoEncontrado("Autor no encontrado")
    return autor


def crear_autor(db: Session, datos: AutorCrear) -> Autor:
    """Crea un nuevo autor validando unicidad de nombre."""
    existente = db.scalar(
        select(Autor).where(func.lower(Autor.nombre) == datos.nombre.lower())
    )
    if existente:
        raise Conflicto("Ya existe un autor con ese nombre")

    nuevo_autor = Autor(
        nombre=datos.nombre,
        nacionalidad=datos.nacionalidad,
        anio_nacimiento=datos.anio_nacimiento
    )
    db.add(nuevo_autor)
    db.commit()
    db.refresh(nuevo_autor)
    return nuevo_autor


def actualizar_autor(db: Session, autor_id: int, datos: AutorActualizar) -> Autor:
    """Actualiza solo los campos enviados del autor validando unicidad."""
    autor = obtener_autor(db, autor_id)

    if datos.nombre is not None:
        existente = db.scalar(
            select(Autor).where(
                func.lower(Autor.nombre) == datos.nombre.lower(),
                Autor.id != autor_id
            )
        )
        if existente:
            raise Conflicto("Ya existe otro autor con ese nombre")
        autor.nombre = datos.nombre

    if datos.nacionalidad is not None:
        autor.nacionalidad = datos.nacionalidad

    if datos.anio_nacimiento is not None:
        autor.anio_nacimiento = datos.anio_nacimiento

    db.commit()
    db.refresh(autor)
    return autor


def eliminar_autor(db: Session, autor_id: int) -> None:
    """Elimina un autor si no tiene libros asociados (409 si tiene libros)."""
    autor = obtener_autor(db, autor_id)

    # Verificar si tiene libros dependientes
    total_libros = db.scalar(
        select(func.count(Libro.id)).where(Libro.autor_id == autor_id)
    )
    if total_libros and total_libros > 0:
        raise Conflicto("No se puede eliminar el autor porque tiene libros asociados")

    db.delete(autor)
    db.commit()
