from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload
from ..core.exceptions import Conflicto, NoEncontrado, ReglaNegocio
from ..models.libro import Libro
from ..models.prestamo import Prestamo
from ..models.socio import Socio
from ..models.usuario import RolUsuario, Usuario
from ..schemas.pagina import Pagina
from ..schemas.prestamo import DevolucionCrear, EstadoPrestamoEnum, PrestamoCrear, PrestamoRespuesta


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
    libro_id: int | None = None,
    usuario_actual: Usuario | None = None
) -> Pagina[PrestamoRespuesta]:
    """
    Lista préstamos paginados con filtros.
    Regla Z3: Si el usuario es un socio, se fuerza el filtrado exclusivamente por sus propios préstamos.
    """
    hoy = date.today()
    consulta = select(Prestamo).options(
        selectinload(Prestamo.libro),
        selectinload(Prestamo.socio)
    )

    # Regla Z3: filtrado forzoso para socios
    if usuario_actual and usuario_actual.rol == RolUsuario.socio:
        consulta = consulta.where(Prestamo.socio_id == usuario_actual.socio_id)
    elif socio_id is not None:
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

    # Conteo total
    conteo_query = select(func.count()).select_from(consulta.subquery())
    total = db.scalar(conteo_query) or 0

    consulta_paginada = consulta.order_by(Prestamo.id.desc()).offset(skip).limit(limit)
    prestamos = list(db.scalars(consulta_paginada).all())
    for p in prestamos:
        _cargar_relaciones_y_estado(p)

    items_schemas = [PrestamoRespuesta.model_validate(p) for p in prestamos]

    return Pagina[PrestamoRespuesta](
        items=items_schemas,
        total=total,
        skip=skip,
        limit=limit
    )


def obtener_prestamo(
    db: Session,
    prestamo_id: int,
    usuario_actual: Usuario | None = None
) -> Prestamo:
    """
    Consulta un préstamo por ID con libro y socio anidados.
    Regla Z2: Si un socio intenta consultar un préstamo ajeno, recibe 404 NoEncontrado.
    """
    consulta = select(Prestamo).options(
        selectinload(Prestamo.libro),
        selectinload(Prestamo.socio)
    ).where(Prestamo.id == prestamo_id)

    prestamo = db.scalar(consulta)
    if not prestamo:
        raise NoEncontrado("Préstamo no encontrado")

    # Regla Z2: Comprobación estricta de propiedad
    if usuario_actual and usuario_actual.rol == RolUsuario.socio:
        if prestamo.socio_id != usuario_actual.socio_id:
            raise NoEncontrado("Préstamo no encontrado")

    return _cargar_relaciones_y_estado(prestamo)


def crear_prestamo(
    db: Session,
    datos: PrestamoCrear,
    registrado_por: Usuario | None = None
) -> Prestamo:
    """
    Registra un préstamo validando las reglas R1 a R11 en estricto orden:
    R1: El socio existe (404)
    R2: El libro existe (404)
    R3: El socio está activo (422)
    R11: El socio no tiene multas pendientes de pago (422)
    R4: El socio no tiene préstamos vencidos (422)
    R5: El socio tiene menos de 3 préstamos sin devolver (422)
    R6: El socio no tiene ya ese mismo libro sin devolver (409)
    R7: El libro tiene ejemplares disponibles (422)
    R8: fecha_limite = fecha_prestamo + dias
    Regla Z7: Asigna registrado_por_id del bibliotecario o admin responsable.
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

    # R11: El socio no debe tener multas pendientes de pago
    multas_pendientes = db.scalar(
        select(func.count(Prestamo.id)).where(
            Prestamo.socio_id == datos.socio_id,
            Prestamo.multa > 0,
            Prestamo.multa_pagada == False
        )
    ) or 0
    if multas_pendientes > 0:
        raise ReglaNegocio("El socio tiene multas pendientes")

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
        multa=Decimal("0.00"),
        multa_pagada=True,  # 0.00 inicia pagada
        registrado_por_id=registrado_por.id if registrado_por else None
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
    R10: Si se devuelve tarde: multa = días de retraso × 0.50 y multa_pagada = False.
         Si se devuelve a tiempo: multa = 0.00 y multa_pagada = True.
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
        prestamo.multa_pagada = False
    else:
        prestamo.multa = Decimal("0.00")
        prestamo.multa_pagada = True

    prestamo.fecha_devolucion = fecha_devolucion
    db.commit()
    db.refresh(prestamo)

    return obtener_prestamo(db, prestamo.id)


def pagar_multa(
    db: Session,
    prestamo_id: int,
    usuario_actual: Usuario
) -> Prestamo:
    """
    Registra el pago de una multa pendiente (Fase 7 - POST /prestamos/{id}/pago-multa).
    Verifica existencia, permiso sobre el préstamo y estado de la multa.
    Lanza 409 Conflicto si la multa ya fue pagada o no tiene multa.
    """
    prestamo = db.get(Prestamo, prestamo_id)
    if not prestamo:
        raise NoEncontrado("Préstamo no encontrado")

    # Comprobación de propiedad para socios (Regla Z2)
    if usuario_actual.rol == RolUsuario.socio and prestamo.socio_id != usuario_actual.socio_id:
        raise NoEncontrado("Préstamo no encontrado")

    # Si no tiene multa o ya está pagada -> 409
    if prestamo.multa <= Decimal("0.00") or prestamo.multa_pagada:
        raise Conflicto("El préstamo no tiene multas pendientes de pago")

    prestamo.multa_pagada = True
    db.commit()
    db.refresh(prestamo)

    return obtener_prestamo(db, prestamo.id, usuario_actual)
