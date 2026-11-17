from decimal import Decimal
from sqlalchemy import Integer, cast, func, select
from sqlalchemy.orm import Session
from ..models.autor import Autor
from ..models.categoria import Categoria
from ..models.libro import Libro, libro_categoria
from ..models.prestamo import Prestamo
from ..models.socio import Socio


def reporte_libros_mas_prestados(db: Session, limite: int = 5) -> list[dict]:
    """Reporte 1: Libros más prestados ordenados de mayor a menor con una sola consulta SQL."""
    consulta = (
        select(
            Libro.id.label("libro_id"),
            Libro.titulo.label("titulo"),
            Autor.nombre.label("autor"),
            func.count(Prestamo.id).label("total_prestamos")
        )
        .join(Autor, Libro.autor_id == Autor.id)
        .join(Prestamo, Prestamo.libro_id == Libro.id)
        .group_by(Libro.id, Libro.titulo, Autor.nombre)
        .order_by(func.count(Prestamo.id).desc())
        .limit(limite)
    )
    filas = db.execute(consulta).all()
    return [fila._asdict() for fila in filas]


def reporte_categorias(db: Session) -> list[dict]:
    """Reporte 2: Total de libros por categoría, incluidas las que tienen 0, en una sola consulta."""
    total = func.count(libro_categoria.c.libro_id).label("total_libros")
    consulta = (
        select(
            Categoria.id.label("categoria_id"),
            Categoria.nombre.label("categoria"),
            total
        )
        .outerjoin(libro_categoria, libro_categoria.c.categoria_id == Categoria.id)
        .group_by(Categoria.id, Categoria.nombre)
        .order_by(Categoria.id.asc())
    )
    filas = db.execute(consulta).all()
    return [fila._asdict() for fila in filas]


def reporte_prestamos_vencidos(db: Session) -> list[dict]:
    """Reporte 3: Préstamos vencidos con título, socio y días de retraso en una sola consulta."""
    dias_retraso = cast(func.current_date() - Prestamo.fecha_limite, Integer).label("dias_retraso")
    consulta = (
        select(
            Prestamo.id.label("prestamo_id"),
            Libro.titulo.label("titulo"),
            Socio.id.label("socio_id"),
            Socio.nombre.label("socio"),
            Socio.email.label("email"),
            Prestamo.fecha_limite.label("fecha_limite"),
            dias_retraso
        )
        .join(Libro, Prestamo.libro_id == Libro.id)
        .join(Socio, Prestamo.socio_id == Socio.id)
        .where(
            Prestamo.fecha_devolucion.is_(None),
            Prestamo.fecha_limite < func.current_date()
        )
        .order_by(dias_retraso.desc())
    )
    filas = db.execute(consulta).all()
    return [fila._asdict() for fila in filas]


def reporte_socios_con_multas(db: Session) -> list[dict]:
    """Reporte 4: Socios con total de multas acumuladas en una sola consulta con HAVING."""
    consulta = (
        select(
            Socio.id.label("socio_id"),
            Socio.nombre.label("socio"),
            Socio.email.label("email"),
            func.sum(Prestamo.multa).label("total_multas"),
            func.count(Prestamo.id).label("prestamos_con_multa")
        )
        .join(Prestamo, Prestamo.socio_id == Socio.id)
        .where(Prestamo.multa > 0)
        .group_by(Socio.id, Socio.nombre, Socio.email)
        .having(func.sum(Prestamo.multa) > 0)
        .order_by(func.sum(Prestamo.multa).desc())
    )
    filas = db.execute(consulta).all()
    return [fila._asdict() for fila in filas]


def reporte_autores(db: Session) -> list[dict]:
    """Reporte 5: Libros, ejemplares y préstamos de cada autor resuelto con outerjoin y count distinct."""
    sub_ejemplares = (
        select(func.coalesce(func.sum(Libro.ejemplares), 0))
        .where(Libro.autor_id == Autor.id)
        .correlate(Autor)
        .scalar_subquery()
    )

    consulta = (
        select(
            Autor.id.label("autor_id"),
            Autor.nombre.label("autor"),
            func.count(func.distinct(Libro.id)).label("total_libros"),
            sub_ejemplares.label("total_ejemplares"),
            func.count(func.distinct(Prestamo.id)).label("total_prestamos")
        )
        .outerjoin(Libro, Libro.autor_id == Autor.id)
        .outerjoin(Prestamo, Prestamo.libro_id == Libro.id)
        .group_by(Autor.id, Autor.nombre)
        .order_by(Autor.id.asc())
    )
    filas = db.execute(consulta).all()
    return [fila._asdict() for fila in filas]


def reporte_resumen(db: Session) -> dict:
    """Reporte 6: Resumen global con totales en una sola consulta SQL."""
    consulta = select(
        select(func.count(Libro.id)).scalar_subquery().label("total_libros"),
        select(func.coalesce(func.sum(Libro.ejemplares), 0)).scalar_subquery().label("total_ejemplares"),
        select(func.count(Prestamo.id)).where(Prestamo.fecha_devolucion.is_(None)).scalar_subquery().label("total_prestados"),
        select(func.count(Socio.id)).where(Socio.activo.is_(True)).scalar_subquery().label("socios_activos"),
        select(func.count(Prestamo.id)).where(
            Prestamo.fecha_devolucion.is_(None),
            Prestamo.fecha_limite < func.current_date()
        ).scalar_subquery().label("prestamos_vencidos"),
        select(func.coalesce(func.sum(Prestamo.multa), Decimal("0.00"))).scalar_subquery().label("total_multas")
    )
    fila = db.execute(consulta).first()
    return fila._asdict() if fila else {}
