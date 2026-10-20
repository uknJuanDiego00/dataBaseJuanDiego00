from fastapi import APIRouter, Query, status
from ..controllers import libro_controller
from ..core.dependencies import PaginacionDep, SessionDep
from ..schemas.libro import (
    LibroActualizar,
    LibroCrear,
    LibroRespuesta,
    OrdenLibrosEnum
)

router = APIRouter(
    prefix="/libros",
    tags=["Libros"]
)


@router.get("", response_model=list[LibroRespuesta], status_code=status.HTTP_200_OK)
def listar_libros(
    db: SessionDep,
    paginacion: PaginacionDep,
    buscar: str | None = Query(default=None, description="Buscar por título (ilike)"),
    autor: str | None = Query(default=None, description="Buscar por nombre del autor (ilike)"),
    categoria_id: int | None = Query(default=None, description="Filtrar por ID de categoría"),
    desde: int | None = Query(default=None, description="Año de publicación inicial"),
    hasta: int | None = Query(default=None, description="Año de publicación final"),
    orden: OrdenLibrosEnum | None = Query(default=None, description="Criterio de ordenación: titulo, anio o -anio")
):
    """Lista paginada de libros con filtros combinables y cálculo de ejemplares disponibles."""
    return libro_controller.listar_libros(
        db=db,
        skip=paginacion.skip,
        limit=paginacion.limit,
        buscar=buscar,
        autor=autor,
        categoria_id=categoria_id,
        desde=desde,
        hasta=hasta,
        orden=orden
    )


@router.get("/{id}", response_model=LibroRespuesta, status_code=status.HTTP_200_OK)
def obtener_libro(id: int, db: SessionDep):
    """Consulta un libro por su ID con autor, categorías y ejemplares disponibles."""
    return libro_controller.obtener_libro(db=db, libro_id=id)


@router.post("", response_model=LibroRespuesta, status_code=status.HTTP_201_CREATED)
def crear_libro(datos: LibroCrear, db: SessionDep):
    """Crea un nuevo libro en el catálogo."""
    return libro_controller.crear_libro(db=db, datos=datos)


@router.patch("/{id}", response_model=LibroRespuesta, status_code=status.HTTP_200_OK)
def actualizar_libro(id: int, datos: LibroActualizar, db: SessionDep):
    """Actualiza los datos de un libro y reemplaza categorías si se enviaron."""
    return libro_controller.actualizar_libro(db=db, libro_id=id, datos=datos)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_libro(id: int, db: SessionDep):
    """Elimina un libro si no tiene préstamos activos."""
    libro_controller.eliminar_libro(db=db, libro_id=id)
    return None
