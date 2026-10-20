from fastapi import APIRouter, Query, status
from ..controllers import socio_controller
from ..core.dependencies import PaginacionDep, SessionDep
from ..schemas.prestamo import EstadoPrestamoEnum, PrestamoRespuesta
from ..schemas.socio import SocioActualizar, SocioCrear, SocioRespuesta

router = APIRouter(
    prefix="/socios",
    tags=["Socios"]
)


@router.get("", response_model=list[SocioRespuesta], status_code=status.HTTP_200_OK)
def listar_socios(
    db: SessionDep,
    paginacion: PaginacionDep,
    activo: bool | None = Query(default=None, description="Filtrar por estado activo/inactivo")
):
    """Lista paginada de socios con filtro opcional por estado."""
    return socio_controller.listar_socios(
        db=db,
        skip=paginacion.skip,
        limit=paginacion.limit,
        activo=activo
    )


@router.get("/{id}", response_model=SocioRespuesta, status_code=status.HTTP_200_OK)
def obtener_socio(id: int, db: SessionDep):
    """Consulta un socio por su ID."""
    return socio_controller.obtener_socio(db=db, socio_id=id)


@router.post("", response_model=SocioRespuesta, status_code=status.HTTP_201_CREATED)
def crear_socio(datos: SocioCrear, db: SessionDep):
    """Crea un nuevo socio en el sistema."""
    return socio_controller.crear_socio(db=db, datos=datos)


@router.patch("/{id}", response_model=SocioRespuesta, status_code=status.HTTP_200_OK)
def actualizar_socio(id: int, datos: SocioActualizar, db: SessionDep):
    """Actualiza los datos de un socio."""
    return socio_controller.actualizar_socio(db=db, socio_id=id, datos=datos)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_socio(id: int, db: SessionDep):
    """
    Elimina un socio:
    - 409 si tiene préstamos activos.
    - Se desactiva si tiene historial de préstamos devueltos.
    - Se elimina físicamente si no tiene préstamos.
    """
    socio_controller.eliminar_socio(db=db, socio_id=id)
    return None


@router.get("/{id}/prestamos", response_model=list[PrestamoRespuesta], status_code=status.HTTP_200_OK)
def listar_prestamos_socio(
    id: int,
    db: SessionDep,
    paginacion: PaginacionDep,
    estado: EstadoPrestamoEnum | None = Query(default=None, description="Filtrar por estado: activo, vencido, devuelto")
):
    """Lista los préstamos de un socio específico."""
    return socio_controller.listar_prestamos_socio(
        db=db,
        socio_id=id,
        skip=paginacion.skip,
        limit=paginacion.limit,
        estado=estado
    )
