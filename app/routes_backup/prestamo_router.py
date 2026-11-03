from fastapi import APIRouter, Depends, Query, status
from ..controllers import prestamo_controller
from ..core.dependencies import PaginacionDep, SessionDep, UsuarioActualDep, requiere_rol
from ..models.usuario import RolUsuario
from ..schemas.pagina import Pagina
from ..schemas.prestamo import (
    DevolucionCrear,
    EstadoPrestamoEnum,
    PrestamoCrear,
    PrestamoRespuesta
)

router = APIRouter(
    prefix="/prestamos",
    tags=["Préstamos"]
)


@router.get(
    "",
    response_model=Pagina[PrestamoRespuesta],
    status_code=status.HTTP_200_OK,
    summary="Listar préstamos paginados",
    responses={
        200: {"description": "Página de préstamos"},
        401: {"description": "No autenticado"}
    }
)
def listar_prestamos(
    db: SessionDep,
    paginacion: PaginacionDep,
    usuario: UsuarioActualDep,
    estado: EstadoPrestamoEnum | None = Query(default=None, description="Filtrar por estado: activo, vencido, devuelto"),
    socio_id: int | None = Query(default=None, description="Filtrar por ID de socio (ignorado si es socio)"),
    libro_id: int | None = Query(default=None, description="Filtrar por ID de libro")
):
    """
    Lista paginada de préstamos con filtros opcionales.
    Regla Z3: Si el usuario autenticado es socio, solo se retornan sus propios préstamos.
    """
    return prestamo_controller.listar_prestamos(
        db=db,
        skip=paginacion.skip,
        limit=paginacion.limit,
        estado=estado,
        socio_id=socio_id,
        libro_id=libro_id,
        usuario_actual=usuario
    )


@router.get(
    "/{id}",
    response_model=PrestamoRespuesta,
    status_code=status.HTTP_200_OK,
    summary="Consultar un préstamo por ID",
    responses={
        200: {"description": "Detalle del préstamo"},
        401: {"description": "No autenticado"},
        404: {"description": "Préstamo no encontrado o no pertenece al socio"}
    }
)
def obtener_prestamo(id: int, db: SessionDep, usuario: UsuarioActualDep):
    """
    Consulta un préstamo por ID con libro y socio anidados.
    Regla Z2: Si un socio consulta un préstamo ajeno, recibe 404 NoEncontrado.
    """
    return prestamo_controller.obtener_prestamo(
        db=db,
        prestamo_id=id,
        usuario_actual=usuario
    )


@router.post(
    "",
    response_model=PrestamoRespuesta,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo préstamo (Bibliotecario o Admin)",
    responses={
        201: {"description": "Préstamo registrado exitosamente"},
        401: {"description": "No autenticado"},
        403: {"description": "Requiere rol bibliotecario o admin"},
        404: {"description": "Socio o libro no encontrado"},
        409: {"description": "El socio ya tiene este libro sin devolver"},
        422: {"description": "Reglas de negocio no cumplidas (ej. multas pendientes, máximo 3 préstamos)"}
    }
)
def crear_prestamo(
    datos: PrestamoCrear,
    db: SessionDep,
    usuario: UsuarioActualDep = Depends(requiere_rol(RolUsuario.bibliotecario, RolUsuario.admin))
):
    """
    Registra un nuevo préstamo validando reglas R1 a R11.
    Regla Z7: Asigna el bibliotecario responsable en registrado_por_id.
    """
    return prestamo_controller.crear_prestamo(
        db=db,
        datos=datos,
        registrado_por=usuario
    )


@router.post(
    "/{id}/devolucion",
    response_model=PrestamoRespuesta,
    status_code=status.HTTP_200_OK,
    summary="Registrar devolución de un libro (Bibliotecario o Admin)",
    responses={
        200: {"description": "Devolución registrada con cálculo de multas"},
        401: {"description": "No autenticado"},
        403: {"description": "Requiere rol bibliotecario o admin"},
        404: {"description": "Préstamo no encontrado"},
        409: {"description": "El préstamo ya fue devuelto"},
        422: {"description": "Fecha de devolución anterior a la de préstamo"}
    }
)
def registrar_devolucion(
    id: int,
    db: SessionDep,
    datos: DevolucionCrear | None = None,
    usuario: UsuarioActualDep = Depends(requiere_rol(RolUsuario.bibliotecario, RolUsuario.admin))
):
    """Registra la devolución calculando multas por retraso (reglas R9 y R10)."""
    return prestamo_controller.registrar_devolucion(db=db, prestamo_id=id, datos=datos)


@router.post(
    "/{id}/pago-multa",
    response_model=PrestamoRespuesta,
    status_code=status.HTTP_200_OK,
    summary="Registrar pago de multa pendiente",
    responses={
        200: {"description": "Multa pagada exitosamente"},
        401: {"description": "No autenticado"},
        404: {"description": "Préstamo no encontrado o no pertenece al socio"},
        409: {"description": "El préstamo no tiene multa pendiente"}
    }
)
def pagar_multa(id: int, db: SessionDep, usuario: UsuarioActualDep):
    """
    Registra el pago de una multa pendiente de un préstamo devuelto con retraso.
    Permitido para el socio titular, bibliotecarios y administradores.
    """
    return prestamo_controller.pagar_multa(db=db, prestamo_id=id, usuario_actual=usuario)
