
from fastapi import APIRouter, Depends, Query, status

from ..controllers import autor_controller, libro_controller
from ..core.dependencies import PaginacionDep, SessionDep, requiere_rol
from ..models.usuario import RolUsuario
from ..schemas.autor import AutorActualizar, AutorCrear, AutorRespuesta
from ..schemas.libro import LibroRespuesta
from ..schemas.pagina import Pagina


router = APIRouter(
    prefix="/autores",
    tags=["Autores"]
)


# ==========================================================
# LISTAR AUTORES
# ==========================================================

@router.get(
    "",
    response_model=Pagina[AutorRespuesta],
    status_code=status.HTTP_200_OK,
    summary="Listar autores paginados",
    responses={
        200: {"description": "Página de autores"}
    }
)
def listar_autores(
    db: SessionDep,
    paginacion: PaginacionDep,
    nacionalidad: str | None = Query(
        default=None,
        description="Filtrar por nacionalidad"
    )
):
    """Lista paginada de autores con filtro opcional por nacionalidad."""
    return autor_controller.listar_autores(
        db=db,
        skip=paginacion.skip,
        limit=paginacion.limit,
        nacionalidad=nacionalidad
    )


# ==========================================================
# OBTENER AUTOR POR ID
# ==========================================================

@router.get(
    "/{id}",
    response_model=AutorRespuesta,
    status_code=status.HTTP_200_OK,
    summary="Consultar un autor por su ID",
    responses={
        200: {"description": "Detalle del autor"},
        404: {"description": "Autor no encontrado"}
    }
)
def obtener_autor(id: int, db: SessionDep):
    """Consulta un autor por su ID."""
    return autor_controller.obtener_autor(
        db=db,
        autor_id=id
    )


# ==========================================================
# CREAR AUTOR
# Acceso: Bibliotecario o Administrador
# ==========================================================

@router.post(
    "",
    response_model=AutorRespuesta,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un autor (Bibliotecario o Admin)",
    dependencies=[
        Depends(
            requiere_rol(
                RolUsuario.bibliotecario,
                RolUsuario.admin
            )
        )
    ],
    responses={
        201: {"description": "Autor creado exitosamente"},
        401: {"description": "No autenticado"},
        403: {"description": "Requiere rol bibliotecario o admin"},
        409: {"description": "Nombre de autor duplicado"}
    }
)
def crear_autor(
    datos: AutorCrear,
    db: SessionDep
):
    """Crea un nuevo autor en el sistema."""
    return autor_controller.crear_autor(
        db=db,
        datos=datos
    )


# ==========================================================
# ACTUALIZAR AUTOR
# Acceso: Bibliotecario o Administrador
# ==========================================================

@router.patch(
    "/{id}",
    response_model=AutorRespuesta,
    status_code=status.HTTP_200_OK,
    summary="Actualizar un autor (Bibliotecario o Admin)",
    dependencies=[
        Depends(
            requiere_rol(
                RolUsuario.bibliotecario,
                RolUsuario.admin
            )
        )
    ],
    responses={
        200: {"description": "Autor actualizado"},
        401: {"description": "No autenticado"},
        403: {"description": "Requiere rol bibliotecario o admin"},
        404: {"description": "Autor no encontrado"},
        409: {"description": "Nombre duplicado"}
    }
)
def actualizar_autor(
    id: int,
    datos: AutorActualizar,
    db: SessionDep
):
    """Actualiza solo los campos enviados de un autor."""
    return autor_controller.actualizar_autor(
        db=db,
        autor_id=id,
        datos=datos
    )


# ==========================================================
# ELIMINAR AUTOR
# Acceso: Solo Administrador
# ==========================================================

@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un autor (Solo Admin)",
    dependencies=[
        Depends(
            requiere_rol(RolUsuario.admin)
        )
    ],
    responses={
        204: {"description": "Autor eliminado"},
        401: {"description": "No autenticado"},
        403: {"description": "Requiere rol admin"},
        404: {"description": "Autor no encontrado"},
        409: {"description": "Tiene libros asociados"}
    }
)
def eliminar_autor(
    id: int,
    db: SessionDep
):
    """Elimina un autor por su ID si no tiene libros dependientes."""
    autor_controller.eliminar_autor(
        db=db,
        autor_id=id
    )
    return None


# ==========================================================
# LISTAR LIBROS DE UN AUTOR
# ==========================================================

@router.get(
    "/{id}/libros",
    response_model=Pagina[LibroRespuesta],
    status_code=status.HTTP_200_OK,
    summary="Listar libros de un autor",
    responses={
        200: {"description": "Página de libros del autor"},
        404: {"description": "Autor no encontrado"}
    }
)
def listar_libros_de_autor(
    id: int,
    db: SessionDep,
    paginacion: PaginacionDep
):
    """Lista los libros de un autor específico con paginación."""
    return libro_controller.listar_libros_por_autor(
        db=db,
        autor_id=id,
        skip=paginacion.skip,
        limit=paginacion.limit
    )
