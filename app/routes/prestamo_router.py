from fastapi import APIRouter, Query, status
from ..controllers import prestamo_controller
from ..core.dependencies import PaginacionDep, SessionDep
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


@router.get("", response_model=list[PrestamoRespuesta], status_code=status.HTTP_200_OK)
def listar_prestamos(
    db: SessionDep,
    paginacion: PaginacionDep,
    estado: EstadoPrestamoEnum | None = Query(default=None, description="Filtrar por estado: activo, vencido, devuelto"),
    socio_id: int | None = Query(default=None, description="Filtrar por ID de socio"),
    libro_id: int | None = Query(default=None, description="Filtrar por ID de libro")
):
    """Lista paginada de préstamos con filtros opcionales."""
    return prestamo_controller.listar_prestamos(
        db=db,
        skip=paginacion.skip,
        limit=paginacion.limit,
        estado=estado,
        socio_id=socio_id,
        libro_id=libro_id
    )


@router.get("/{id}", response_model=PrestamoRespuesta, status_code=status.HTTP_200_OK)
def obtener_prestamo(id: int, db: SessionDep):
    """Consulta un préstamo por ID con libro y socio anidados."""
    return prestamo_controller.obtener_prestamo(db=db, prestamo_id=id)


@router.post("", response_model=PrestamoRespuesta, status_code=status.HTTP_201_CREATED)
def crear_prestamo(datos: PrestamoCrear, db: SessionDep):
    """Registra un nuevo préstamo validando reglas de negocio R1 a R8."""
    return prestamo_controller.crear_prestamo(db=db, datos=datos)


@router.post("/{id}/devolucion", response_model=PrestamoRespuesta, status_code=status.HTTP_200_OK)
def registrar_devolucion(
    id: int,
    db: SessionDep,
    datos: DevolucionCrear | None = None
):
    """Registra la devolución de un préstamo calculando multas por retraso (reglas R9 y R10)."""
    return prestamo_controller.registrar_devolucion(db=db, prestamo_id=id, datos=datos)
