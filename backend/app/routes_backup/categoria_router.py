from fastapi import APIRouter, Depends, status
from ..controllers import categoria_controller
from ..core.dependencies import PaginacionDep, SessionDep, UsuarioActualDep, requiere_rol
from ..models.usuario import RolUsuario
from ..schemas.categoria import (
    CategoriaActualizar,
    CategoriaCrear,
    CategoriaRespuesta
)
from ..schemas.pagina import Pagina

router = APIRouter(
    prefix="/categorias",
    tags=["Categorías"]
)


@router.get(
    "",
    response_model=Pagina[CategoriaRespuesta],
    status_code=status.HTTP_200_OK,
    summary="Listar categorías paginadas",
    responses={
        200: {"description": "Página de categorías registradas"}
    }
)
def listar_categorias(db: SessionDep, paginacion: PaginacionDep):
    """Lista paginada de categorías registradas en la biblioteca."""
    return categoria_controller.listar_categorias(
        db=db,
        skip=paginacion.skip,
        limit=paginacion.limit
    )


@router.get(
    "/{id}",
    response_model=CategoriaRespuesta,
    status_code=status.HTTP_200_OK,
    summary="Consultar una categoría por su ID",
    responses={
        200: {"description": "Detalle de la categoría"},
        404: {"description": "Categoría no encontrada"}
    }
)
def obtener_categoria(id: int, db: SessionDep):
    """Consulta una categoría por su ID."""
    return categoria_controller.obtener_categoria(db=db, categoria_id=id)


@router.post(
    "",
    response_model=CategoriaRespuesta,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva categoría (Bibliotecario o Admin)",
    responses={
        201: {"description": "Categoría creada exitosamente"},
        401: {"description": "No autenticado"},
        403: {"description": "Requiere rol bibliotecario o admin"},
        409: {"description": "Nombre de categoría duplicado"}
    }
)
def crear_categoria(
    datos: CategoriaCrear,
    db: SessionDep,
    usuario: UsuarioActualDep = Depends(requiere_rol(RolUsuario.bibliotecario, RolUsuario.admin))
):
    """Crea una nueva categoría en minúsculas y sin espacios sobrantes."""
    return categoria_controller.crear_categoria(db=db, datos=datos)


@router.patch(
    "/{id}",
    response_model=CategoriaRespuesta,
    status_code=status.HTTP_200_OK,
    summary="Actualizar una categoría (Bibliotecario o Admin)",
    responses={
        200: {"description": "Categoría actualizada"},
        401: {"description": "No autenticado"},
        403: {"description": "Requiere rol bibliotecario o admin"},
        404: {"description": "Categoría no encontrada"},
        409: {"description": "Nombre de categoría duplicado"}
    }
)
def actualizar_categoria(
    id: int,
    datos: CategoriaActualizar,
    db: SessionDep,
    usuario: UsuarioActualDep = Depends(requiere_rol(RolUsuario.bibliotecario, RolUsuario.admin))
):
    """Actualiza los datos de una categoría."""
    return categoria_controller.actualizar_categoria(db=db, categoria_id=id, datos=datos)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una categoría (Solo Admin)",
    responses={
        204: {"description": "Categoría eliminada"},
        401: {"description": "No autenticado"},
        403: {"description": "Requiere rol admin"},
        404: {"description": "Categoría no encontrada"}
    }
)
def eliminar_categoria(
    id: int,
    db: SessionDep,
    usuario: UsuarioActualDep = Depends(requiere_rol(RolUsuario.admin))
):
    """Elimina una categoría y la retira de los libros que la tenían."""
    categoria_controller.eliminar_categoria(db=db, categoria_id=id)
    return None
