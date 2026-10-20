from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload
from ..core.exceptions import Conflicto, NoEncontrado, ReglaNegocio
from ..models.libro import Libro
from ..models.prestamo import Prestamo
from ..models.socio import Socio
from ..schemas.prestamo import DevolucionCrear, EstadoPrestamoEnum, PrestamoCrear


def calcular_estado(prestamo: Prestamo) -> str:
    """Calcula el estado del préstamo dinámicamente a partir de las fechas."""
    if prestamo.fecha_devolucion is not None:
        return "devuelto"
    if prestamo.fecha_limite < date.today():
        return "vencido"
    return "activo"


def _cargar_relaciones_y_estado(prestamo: Prestamo) -> Prestamo:
    """Asigna el estado calculado al préstamo."""
    prestamo.estado = calcular_estado(prestamo)
    return prestamo


def listar_prestamos(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    estado: EstadoPrestamoEnum | None = None,
    socio_id: int | None = None,
    libro_id: int | None = None
) -> list[Prestamo]:
    """Lista préstamos paginados con filtros por estado, socio y libro."""
    hoy = date.today()
    consulta = select(Prestamo).options(
        selectinload(Prestamo.libro),
        selectinload(Prestamo.socio)
    )

    if socio_id is not None:
        consulta = consulta.where(Prestamo.socio_id == socio_id)

    if libro_id is not None:
        consulta = consulta.where(Prestamo.libro_id == libro_id)

    if estado == EstadoPrestamoEnum.devuelto:
        consulta = consulta.where(Prestamo.fecha_devolucion.is_not(None))
    elif estado == EstadoPrestamoEnum.vencido:
        consulta = consulta.where(
            Prestamo.fecha_devolucion.is_(None),
            Prestamo.fecha_limite < hoy
        )
    elif estado == EstadoPrestamoEnum.activo:
        consulta = consulta.where(
            Prestamo.fecha_devolucion.is_(None),
            Prestamo.fecha_limite >= hoy
        )

    consulta = consulta.order_by(Prestamo.id.desc()).offset(skip).limit(limit)
    prestamos = list(db.scalars(consulta).all())
    for p in prestamos:
        _cargar_relaciones_y_estado(p)
    return prestamos


def obtener_prestamo(db: Session, prestamo_id: int) -> Prestamo:
    """Consulta un préstamo por ID con libro y socio anidados."""
    consulta = select(Prestamo).options(
        selectinload(Prestamo.libro),
        selectinload(Prestamo.socio)
    ).where(Prestamo.id == prestamo_id)

    prestamo = db.scalar(consulta)
    if not prestamo:
        raise NoEncontrado("Préstamo no encontrado")

    return _cargar_relaciones_y_estado(prestamo)


def crear_prestamo(db: Session, datos: PrestamoCrear) -> Prestamo:
    """
    Registra un préstamo validando las reglas R1 a R8 en estricto orden:
    R1: El socio existe (404)
    R2: El libro existe (404)
    R3: El socio está activo (422)
    R4: El socio no tiene préstamos vencidos (422)
    R5: El socio tiene menos de 3 préstamos sin devolver (422)
    R6: El socio no tiene ya ese mismo libro sin devolver (409)
    R7: El libro tiene ejemplares disponibles (422)
    R8: fecha_limite = fecha_prestamo + dias
    """
    hoy = date.today()

    # R1: El socio existe
    socio = db.get(Socio, datos.socio_id)
    if not socio:
        raise NoEncontrado("Socio no encontrado")

    # R2: El libro existe
    libro = db.get(Libro, datos.libro_id)
    if not libro:
        raise NoEncontrado("Libro no encontrado")

    # R3: El socio está activo
    if not socio.activo:
        raise ReglaNegocio("El socio no está activo")

    # R4: El socio no tiene préstamos vencidos
    vencidos = db.scalar(
        select(func.count(Prestamo.id)).where(
            Prestamo.socio_id == datos.socio_id,
            Prestamo.fecha_devolucion.is_(None),
            Prestamo.fecha_limite < hoy
        )
    ) or 0
    if vencidos > 0:
        raise ReglaNegocio("El socio tiene préstamos vencidos")

    # R5: El socio tiene menos de 3 préstamos sin devolver
    sin_devolver = db.scalar(
        select(func.count(Prestamo.id)).where(
            Prestamo.socio_id == datos.socio_id,
            Prestamo.fecha_devolucion.is_(None)
        )
    ) or 0
    if sin_devolver >= 3:
        raise ReglaNegocio("Máximo de 3 préstamos")

    # R6: El socio no tiene ya ese mismo libro sin devolver
    mismo_libro = db.scalar(
        select(func.count(Prestamo.id)).where(
            Prestamo.socio_id == datos.socio_id,
            Prestamo.libro_id == datos.libro_id,
            Prestamo.fecha_devolucion.is_(None)
        )
    ) or 0
    if mismo_libro > 0:
        raise Conflicto("El socio ya tiene este libro sin devolver")

    # R7: El libro tiene ejemplares disponibles
    prestamos_activos_libro = db.scalar(
        select(func.count(Prestamo.id)).where(
            Prestamo.libro_id == datos.libro_id,
            Prestamo.fecha_devolucion.is_(None)
        )
    ) or 0
    disponibles = libro.ejemplares - prestamos_activos_libro
    if disponibles <= 0:
        raise ReglaNegocio("No hay ejemplares disponibles")

    # R8: fecha_limite = fecha_prestamo + dias
    fecha_limite = datos.fecha_prestamo + timedelta(days=datos.dias)

    nuevo_prestamo = Prestamo(
        libro_id=datos.libro_id,
        socio_id=datos.socio_id,
        fecha_prestamo=datos.fecha_prestamo,
        fecha_limite=fecha_limite,
        fecha_devolucion=None,
        multa=Decimal("0.00")
    )
    db.add(nuevo_prestamo)
    db.commit()
    db.refresh(nuevo_prestamo)

    return obtener_prestamo(db, nuevo_prestamo.id)


def registrar_devolucion(
    db: Session,
    prestamo_id: int,
    datos: DevolucionCrear | None = None
) -> Prestamo:
    """
    Registra la devolución aplicando las reglas R9 y R10:
    R9: El préstamo existe (404), no fue devuelto antes (409) y fecha no es anterior al préstamo (422)
    R10: Si se devuelve tarde: multa = días de retraso × 0.50
    """
    prestamo = db.get(Prestamo, prestamo_id)
    if not prestamo:
        raise NoEncontrado("Préstamo no encontrado")

    if prestamo.fecha_devolucion is not None:
        raise Conflicto("El préstamo ya fue devuelto")

    fecha_devolucion = datos.fecha_devolucion if datos and datos.fecha_devolucion else date.today()

    if fecha_devolucion < prestamo.fecha_prestamo:
        raise ReglaNegocio("La fecha de devolución no puede ser anterior a la fecha de préstamo")

    # R10: Cálculo de multa si hay retraso respecto a la fecha_limite
    if fecha_devolucion > prestamo.fecha_limite:
        dias_retraso = (fecha_devolucion - prestamo.fecha_limite).days
        prestamo.multa = Decimal(str(dias_retraso)) * Decimal("0.50")
    else:
        prestamo.multa = Decimal("0.00")

    prestamo.fecha_devolucion = fecha_devolucion
    db.commit()
    db.refresh(prestamo)

    return obtener_prestamo(db, prestamo.id)
