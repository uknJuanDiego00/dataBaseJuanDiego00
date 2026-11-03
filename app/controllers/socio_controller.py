from datetime import date
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload
from ..core.exceptions import Conflicto, NoEncontrado
from ..models.prestamo import Prestamo
from ..models.socio import Socio
from ..schemas.pagina import Pagina
from ..schemas.prestamo import EstadoPrestamoEnum, PrestamoRespuesta
from ..schemas.socio import SocioActualizar, SocioCrear, SocioMeActualizar, SocioRespuesta


def listar_socios(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    activo: bool | None = None
) -> Pagina[SocioRespuesta]:
    """Retorna una página de socios con filtro opcional por estado activo."""
    consulta = select(Socio)
    if activo is not None:
        consulta = consulta.where(Socio.activo == activo)

    conteo_query = select(func.count()).select_from(consulta.subquery())
    total = db.scalar(conteo_query) or 0

    items = list(db.scalars(consulta.order_by(Socio.id.asc()).offset(skip).limit(limit)).all())
    items_schemas = [SocioRespuesta.model_validate(s) for s in items]

    return Pagina[SocioRespuesta](
        items=items_schemas,
        total=total,
        skip=skip,
        limit=limit
    )


def obtener_socio(db: Session, socio_id: int) -> Socio:
    """Consulta un socio por su ID o lanza NoEncontrado si no existe."""
    socio = db.get(Socio, socio_id)
    if not socio:
        raise NoEncontrado("Socio no encontrado")
    return socio


def crear_socio(db: Session, datos: SocioCrear) -> Socio:
    """Crea un nuevo socio validando unicidad de correo electrónico."""
    existente = db.scalar(
        select(Socio).where(func.lower(Socio.email) == datos.email.lower())
    )
    if existente:
        raise Conflicto("Ya existe un socio con ese correo electrónico")

    nuevo_socio = Socio(
        nombre=datos.nombre,
        email=datos.email,
        telefono=datos.telefono,
        activo=datos.activo
    )
    db.add(nuevo_socio)
    db.commit()
    db.refresh(nuevo_socio)
    return nuevo_socio


def actualizar_socio(
    db: Session,
    socio_id: int,
    datos: SocioActualizar
) -> Socio:
    """Actualiza solo los campos enviados validando duplicados de email."""
    socio = obtener_socio(db, socio_id)

    if datos.email is not None:
        existente = db.scalar(
            select(Socio).where(
                func.lower(Socio.email) == datos.email.lower(),
                Socio.id != socio_id
            )
        )
        if existente:
            raise Conflicto("Ya existe otro socio con ese correo electrónico")
        socio.email = datos.email

    if datos.nombre is not None:
        socio.nombre = datos.nombre

    if datos.telefono is not None:
        socio.telefono = datos.telefono

    if datos.activo is not None:
        socio.activo = datos.activo

    db.commit()
    db.refresh(socio)
    return socio


def actualizar_socio_me(
    db: Session,
    socio_id: int,
    datos: SocioMeActualizar
) -> Socio:
    """
    Actualiza el perfil propio de un socio.
    Regla Z4: Los socios no pueden modificar email, rol ni activo.
    """
    socio = obtener_socio(db, socio_id)

    if datos.nombre is not None:
        socio.nombre = datos.nombre
    if datos.telefono is not None:
        socio.telefono = datos.telefono

    db.commit()
    db.refresh(socio)
    return socio


def eliminar_socio(db: Session, socio_id: int) -> None:
    """
    Elimina un socio:
    - 409 si tiene préstamos sin devolver.
    - Si solo tiene préstamos devueltos, se desactiva (borrado lógico).
    - Si no tiene préstamos, se elimina físicamente de la base de datos.
    """
    socio = obtener_socio(db, socio_id)

    # 1. Comprobar si tiene préstamos activos / sin devolver
    prestamos_sin_devolver = db.scalar(
        select(func.count(Prestamo.id)).where(
            Prestamo.socio_id == socio_id,
            Prestamo.fecha_devolucion.is_(None)
        )
    ) or 0
    if prestamos_sin_devolver > 0:
        raise Conflicto("No se puede eliminar el socio porque tiene préstamos sin devolver")

    # 2. Comprobar historial devuelto
    total_prestamos = db.scalar(
        select(func.count(Prestamo.id)).where(Prestamo.socio_id == socio_id)
    ) or 0

    if total_prestamos > 0:
        socio.activo = False
        db.commit()
    else:
        db.delete(socio)
        db.commit()


def listar_prestamos_socio(
    db: Session,
    socio_id: int,
    skip: int = 0,
    limit: int = 10,
    estado: EstadoPrestamoEnum | None = None
) -> Pagina[PrestamoRespuesta]:
    """Lista los préstamos de un socio con paginación y filtro opcional de estado."""
    obtener_socio(db, socio_id)

    hoy = date.today()
    consulta = select(Prestamo).options(
        selectinload(Prestamo.libro),
        selectinload(Prestamo.socio)
    ).where(Prestamo.socio_id == socio_id)

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

    conteo_query = select(func.count()).select_from(consulta.subquery())
    total = db.scalar(conteo_query) or 0

    consulta_paginada = consulta.order_by(Prestamo.id.desc()).offset(skip).limit(limit)
    prestamos = list(db.scalars(consulta_paginada).all())

    for p in prestamos:
        if p.fecha_devolucion is not None:
            p.estado = "devuelto"
        elif p.fecha_limite < hoy:
            p.estado = "vencido"
        else:
            p.estado = "activo"

    items_schemas = [PrestamoRespuesta.model_validate(p) for p in prestamos]

    return Pagina[PrestamoRespuesta](
        items=items_schemas,
        total=total,
        skip=skip,
        limit=limit
    )


def listar_multas_socio(
    db: Session,
    socio_id: int,
    skip: int = 0,
    limit: int = 10
) -> Pagina[PrestamoRespuesta]:
    """Retorna los préstamos con multas asociadas al socio especificado."""
    obtener_socio(db, socio_id)

    consulta = select(Prestamo).options(
        selectinload(Prestamo.libro),
        selectinload(Prestamo.socio)
    ).where(
        Prestamo.socio_id == socio_id,
        Prestamo.multa > 0
    )

    conteo_query = select(func.count()).select_from(consulta.subquery())
    total = db.scalar(conteo_query) or 0

    prestamos = list(db.scalars(consulta.order_by(Prestamo.id.desc()).offset(skip).limit(limit)).all())
    hoy = date.today()
    for p in prestamos:
        if p.fecha_devolucion is not None:
            p.estado = "devuelto"
        elif p.fecha_limite < hoy:
            p.estado = "vencido"
        else:
            p.estado = "activo"

    items_schemas = [PrestamoRespuesta.model_validate(p) for p in prestamos]

    return Pagina[PrestamoRespuesta](
        items=items_schemas,
        total=total,
        skip=skip,
        limit=limit
    )
