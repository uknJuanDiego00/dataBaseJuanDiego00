
from fastapi import APIRouter, Depends, status

from ..controllers import categoria_controller
from ..core.dependencies import (
    PaginacionDep,
    SessionDep,
    requiere_rol
)
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


# ==========================================================
# LISTAR CATEGORÍAS
# Acceso: Público
# ==========================================================

@router.get(
    "",
    response_model=Pagina[CategoriaRespuesta],
    status_code=status.HTTP_200_OK
)
def listar_categorias(
    db: SessionDep,
    paginacion: PaginacionDep
):
    """Lista todas las categorías de forma paginada."""
    return categoria_controller.listar_categorias(
        db=db,
        skip=paginacion.skip,
        limit=paginacion.limit
    )


# ==========================================================
# CREAR CATEGORÍA
# Acceso: Bibliotecario o Administrador
# ==========================================================

@router.post(
    "",
    response_model=CategoriaRespuesta,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(
            requiere_rol(
                RolUsuario.bibliotecario,
                RolUsuario.admin
            )
        )
    ]
)
def crear_categoria(
    datos: CategoriaCrear,
    db: SessionDep
):
    """Crea una nueva categoría."""
    return categoria_controller.crear_categoria(
        db=db,
        datos=datos
    )


# ==========================================================
# ELIMINAR CATEGORÍA
# Acceso: Solo Administrador
# ==========================================================

@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(
            requiere_rol(RolUsuario.admin)
        )
    ]
)
def eliminar_categoria(
    id: int,
    db: SessionDep
):
    """Elimina una categoría (Solo Admin)."""
    categoria_controller.eliminar_categoria(
        db=db,
        categoria_id=id
    )
    return None
