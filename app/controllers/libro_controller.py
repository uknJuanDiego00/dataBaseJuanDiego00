from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload
from ..core.exceptions import Conflicto, NoEncontrado, ReglaNegocio
from ..models.autor import Autor
from ..models.categoria import Categoria
from ..models.libro import Libro
from ..models.prestamo import Prestamo
from ..schemas.libro import LibroActualizar, LibroCrear, OrdenLibrosEnum


def _asignar_disponibles(db: Session, libro: Libro) -> None:
    """Calcula y asigna el atributo dinámico disponibles en la instancia del libro."""
    prestamos_activos = db.scalar(
        select(func.count(Prestamo.id)).where(
            Prestamo.libro_id == libro.id,
            Prestamo.fecha_devolucion.is_(None)
        )
    ) or 0
    libro.disponibles = max(0, libro.ejemplares - prestamos_activos)


def listar_libros(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    buscar: str | None = None,
    autor: str | None = None,
    categoria_id: int | None = None,
    desde: int | None = None,
    hasta: int | None = None,
    orden: OrdenLibrosEnum | None = None
) -> list[Libro]:
    """Retorna una lista paginada de libros con filtros combinables y ordenamiento."""
    consulta = select(Libro).options(
        selectinload(Libro.autor),
        selectinload(Libro.categorias)
    )

    if buscar:
        consulta = consulta.where(Libro.titulo.ilike(f"%{buscar.strip()}%"))

    if autor:
        consulta = consulta.join(Libro.autor).where(Autor.nombre.ilike(f"%{autor.strip()}%"))

    if categoria_id is not None:
        consulta = consulta.join(Libro.categorias).where(Categoria.id == categoria_id)

    if desde is not None:
        consulta = consulta.where(Libro.anio_publicacion >= desde)

    if hasta is not None:
        consulta = consulta.where(Libro.anio_publicacion <= hasta)

    # Ordenamiento
    if orden == OrdenLibrosEnum.titulo:
        consulta = consulta.order_by(Libro.titulo.asc())
    elif orden == OrdenLibrosEnum.anio:
        consulta = consulta.order_by(Libro.anio_publicacion.asc())
    elif orden == OrdenLibrosEnum.menos_anio:
        consulta = consulta.order_by(Libro.anio_publicacion.desc())
    else:
        consulta = consulta.order_by(Libro.id.asc())

    libros = list(db.scalars(consulta.offset(skip).limit(limit)).all())
    for lib in libros:
        _asignar_disponibles(db, lib)
    return libros


def obtener_libro(db: Session, libro_id: int) -> Libro:
    """Consulta un libro por ID con autor, categorías y disponibles calculados."""
    consulta = select(Libro).options(
        selectinload(Libro.autor),
        selectinload(Libro.categorias)
    ).where(Libro.id == libro_id)

    libro = db.scalar(consulta)
    if not libro:
        raise NoEncontrado("Libro no encontrado")

    _asignar_disponibles(db, libro)
    return libro


def crear_libro(db: Session, datos: LibroCrear) -> Libro:
    """Crea un nuevo libro asociando autor y categorías validadas."""
    # R1: Validar que el autor exista
    autor = db.get(Autor, datos.autor_id)
    if not autor:
        raise NoEncontrado("Autor no encontrado")

    # Validar que todas las categorías existan
    categorias = list(
        db.scalars(select(Categoria).where(Categoria.id.in_(datos.categoria_ids))).all()
    )
    if len(categorias) != len(datos.categoria_ids):
        raise NoEncontrado("Una o más categorías no existen")

    # Validar unicidad del ISBN
    isbn_existente = db.scalar(
        select(Libro).where(Libro.isbn == datos.isbn)
    )
    if isbn_existente:
        raise Conflicto("Ya existe un libro con ese ISBN")

    nuevo_libro = Libro(
        titulo=datos.titulo,
        isbn=datos.isbn,
        anio_publicacion=datos.anio_publicacion,
        ejemplares=datos.ejemplares,
        autor_id=datos.autor_id,
        categorias=categorias
    )
    db.add(nuevo_libro)
    db.commit()
    db.refresh(nuevo_libro)

    # Cargar relaciones y calcular disponibles
    nuevo_libro = obtener_libro(db, nuevo_libro.id)
    return nuevo_libro


def actualizar_libro(db: Session, libro_id: int, datos: LibroActualizar) -> Libro:
    """Actualiza los datos de un libro y reemplaza categorías si se enviaron."""
    libro = db.scalar(
        select(Libro).options(
            selectinload(Libro.autor),
            selectinload(Libro.categorias)
        ).where(Libro.id == libro_id)
    )
    if not libro:
        raise NoEncontrado("Libro no encontrado")

    if datos.isbn is not None:
        isbn_existente = db.scalar(
            select(Libro).where(Libro.isbn == datos.isbn, Libro.id != libro_id)
        )
        if isbn_existente:
            raise Conflicto("Ya existe otro libro con ese ISBN")
        libro.isbn = datos.isbn

    if datos.autor_id is not None:
        autor = db.get(Autor, datos.autor_id)
        if not autor:
            raise NoEncontrado("Autor no encontrado")
        libro.autor_id = datos.autor_id

    if datos.categoria_ids is not None:
        categorias = list(
            db.scalars(select(Categoria).where(Categoria.id.in_(datos.categoria_ids))).all()
        )
        if len(categorias) != len(datos.categoria_ids):
            raise NoEncontrado("Una o más categorías no existen")
        libro.categorias = categorias

    if datos.ejemplares is not None:
        if datos.ejemplares < 1:
            raise ReglaNegocio("Los ejemplares deben estar entre 1 y 50")

        # Comprobar que no quede por debajo de préstamos sin devolver
        prestamos_activos = db.scalar(
            select(func.count(Prestamo.id)).where(
                Prestamo.libro_id == libro_id,
                Prestamo.fecha_devolucion.is_(None)
            )
        ) or 0
        if datos.ejemplares < prestamos_activos:
            raise ReglaNegocio("Los ejemplares no pueden quedar por debajo de los préstamos activos")
        libro.ejemplares = datos.ejemplares

    if datos.titulo is not None:
        libro.titulo = datos.titulo

    if datos.anio_publicacion is not None:
        libro.anio_publicacion = datos.anio_publicacion

    db.commit()
    return obtener_libro(db, libro.id)


def eliminar_libro(db: Session, libro_id: int) -> None:
    """Elimina un libro si no tiene préstamos sin devolver (409 si tiene)."""
    libro = db.get(Libro, libro_id)
    if not libro:
        raise NoEncontrado("Libro no encontrado")

    prestamos_sin_devolver = db.scalar(
        select(func.count(Prestamo.id)).where(
            Prestamo.libro_id == libro_id,
            Prestamo.fecha_devolucion.is_(None)
        )
    ) or 0
    if prestamos_sin_devolver > 0:
        raise Conflicto("No se puede eliminar el libro porque tiene préstamos sin devolver")

    # Si tiene préstamos devueltos en historial, se pueden eliminar o limpiar
    prestamos_devueltos = list(
        db.scalars(select(Prestamo).where(Prestamo.libro_id == libro_id)).all()
    )
    for p in prestamos_devueltos:
        db.delete(p)

    db.delete(libro)
    db.commit()


def listar_libros_por_autor(
    db: Session,
    autor_id: int,
    skip: int = 0,
    limit: int = 10
) -> list[Libro]:
    """Lista los libros pertenecientes a un autor específico."""
    autor = db.get(Autor, autor_id)
    if not autor:
        raise NoEncontrado("Autor no encontrado")

    consulta = select(Libro).options(
        selectinload(Libro.autor),
        selectinload(Libro.categorias)
    ).where(Libro.autor_id == autor_id).order_by(Libro.id.asc()).offset(skip).limit(limit)

    libros = list(db.scalars(consulta).all())
    for lib in libros:
        _asignar_disponibles(db, lib)
    return libros
