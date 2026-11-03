
from fastapi import APIRouter, Depends, Query, status

from ..controllers import libro_controller
from ..core.dependencies import PaginacionDep, SessionDep, requiere_rol
from ..models.usuario import RolUsuario
from ..schemas.libro import (
    LibroActualizar,
    LibroCrear,
    LibroRespuesta,
    OrdenLibrosEnum
)
from ..schemas.pagina import Pagina


router = APIRouter(
    prefix="/libros",
    tags=["Libros"]
)


# ==========================================================
# LISTAR LIBROS
# Acceso: Público
# ==========================================================

@router.get(
    "",
    response_model=Pagina[LibroRespuesta],
    status_code=status.HTTP_200_OK,
    summary="Catálogo de libros paginado con filtros",
    responses={
        200: {"description": "Página del catálogo de libros"}
    }
)
def listar_libros(
    db: SessionDep,
    paginacion: PaginacionDep,
    buscar: str | None = Query(
        default=None,
        description="Buscar por título (ilike)"
    ),
    autor: str | None = Query(
        default=None,
        description="Buscar por nombre del autor (ilike)"
    ),
    categoria_id: int | None = Query(
        default=None,
        description="Filtrar por ID de categoría"
    ),
    desde: int | None = Query(
        default=None,
        description="Año de publicación inicial"
    ),
    hasta: int | None = Query(
        default=None,
        description="Año de publicación final"
    ),
    orden: OrdenLibrosEnum | None = Query(
        default=None,
        description="Criterio de ordenación: titulo, anio o -anio"
    )
):
    """Lista libros paginados con filtros combinables."""
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


# ==========================================================
# OBTENER LIBRO POR ID
# Acceso: Público
# ==========================================================

@router.get(
    "/{id}",
    response_model=LibroRespuesta,
    status_code=status.HTTP_200_OK,
    summary="Consultar un libro por ID",
    responses={
        200: {"description": "Detalle del libro"},
        404: {"description": "Libro no encontrado"}
    }
)
def obtener_libro(
    id: int,
    db: SessionDep
):
    """Consulta un libro por su ID."""
    return libro_controller.obtener_libro(
        db=db,
        libro_id=id
    )


# ==========================================================
# CREAR LIBRO
# Acceso: Bibliotecario o Administrador
# ==========================================================

@router.post(
    "",
    response_model=LibroRespuesta,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo libro (Bibliotecario o Admin)",
    dependencies=[
        Depends(
            requiere_rol(
                RolUsuario.bibliotecario,
                RolUsuario.admin
            )
        )
    ],
    responses={
        201: {"description": "Libro creado exitosamente"},
        401: {"description": "No autenticado"},
        403: {"description": "Requiere rol bibliotecario o admin"},
        404: {"description": "Autor o categoría no encontrada"},
        409: {"description": "Código ISBN duplicado"}
    }
)
def crear_libro(
    datos: LibroCrear,
    db: SessionDep
):
    """Crea un nuevo libro en el catálogo."""
    return libro_controller.crear_libro(
        db=db,
        datos=datos
    )


# ==========================================================
# ACTUALIZAR LIBRO
# Acceso: Bibliotecario o Administrador
# ==========================================================

@router.patch(
    "/{id}",
    response_model=LibroRespuesta,
    status_code=status.HTTP_200_OK,
    summary="Actualizar un libro (Bibliotecario o Admin)",
    dependencies=[
        Depends(
            requiere_rol(
                RolUsuario.bibliotecario,
                RolUsuario.admin
            )
        )
    ],
    responses={
        200: {"description": "Libro actualizado"},
        401: {"description": "No autenticado"},
        403: {"description": "Requiere rol bibliotecario o admin"},
        404: {"description": "Libro no encontrado"},
        422: {"description": "Cantidad de ejemplares menor a préstamos activos"}
    }
)
def actualizar_libro(
    id: int,
    datos: LibroActualizar,
    db: SessionDep
):
    """Actualiza solo los campos enviados de un libro."""
    return libro_controller.actualizar_libro(
        db=db,
        libro_id=id,
        datos=datos
    )


# ==========================================================
# ELIMINAR LIBRO
# Acceso: Solo Administrador
# ==========================================================

@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un libro (Solo Admin)",
    dependencies=[
        Depends(
            requiere_rol(RolUsuario.admin)
        )
    ],
    responses={
        204: {"description": "Libro eliminado"},
        401: {"description": "No autenticado"},
        403: {"description": "Requiere rol admin"},
        404: {"description": "Libro no encontrado"},
        409: {"description": "Tiene préstamos activos sin devolver"}
    }
)
def eliminar_libro(
    id: int,
    db: SessionDep
):
    """Elimina un libro si no tiene préstamos activos pendientes."""
    libro_controller.eliminar_libro(
        db=db,
        libro_id=id
    )
    return None
