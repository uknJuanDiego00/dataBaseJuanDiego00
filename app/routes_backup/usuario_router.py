from fastapi import APIRouter, Depends, Query, status

from ..controllers import usuario_controller
from ..core.dependencies import PaginacionDep, SessionDep, UsuarioActualDep, requiere_rol
from ..models.usuario import RolUsuario
from ..schemas.pagina import Pagina
from ..schemas.usuario import (
    UsuarioActualizarActivo,
    UsuarioActualizarRol,
    UsuarioCrear,
    UsuarioRespuesta
)

router = APIRouter(
    prefix="/api/v1/usuarios",
    tags=["Usuarios (Administración)"],
    dependencies=[Depends(requiere_rol(RolUsuario.admin))]
)


@router.get(
    "",
    response_model=Pagina[UsuarioRespuesta],
    status_code=status.HTTP_200_OK,
    summary="Listar usuarios paginados (Solo Admin)",
    responses={
        200: {"description": "Página de usuarios"},
        401: {"description": "No autenticado"},
        403: {"description": "Requiere rol admin"}
    }
)
def listar_usuarios(
    db: SessionDep,
    paginacion: PaginacionDep,
    rol: RolUsuario | None = Query(default=None, description="Filtrar por rol"),
    activo: bool | None = Query(default=None, description="Filtrar por estado activo/inactivo")
):
    """Retorna una página de usuarios registrados con total de registros."""
    return usuario_controller.listar_usuarios(
        db=db,
        skip=paginacion.skip,
        limit=paginacion.limit,
        rol=rol,
        activo=activo
    )


@router.post(
    "",
    response_model=UsuarioRespuesta,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un usuario nuevo (Solo Admin)",
    responses={
        201: {"description": "Usuario creado"},
        400: {"description": "Datos inválidos"},
        401: {"description": "No autenticado"},
        403: {"description": "Requiere rol admin"},
        409: {"description": "Correo ya registrado"}
    }
)
def crear_usuario(datos: UsuarioCrear, db: SessionDep):
    """Crea un nuevo usuario en el sistema con el rol especificado."""
    return usuario_controller.crear_usuario(db=db, datos=datos)


@router.patch(
    "/{id}/rol",
    response_model=UsuarioRespuesta,
    status_code=status.HTTP_200_OK,
    summary="Cambiar rol de un usuario (Solo Admin)",
    responses={
        200: {"description": "Rol actualizado"},
        401: {"description": "No autenticado"},
        403: {"description": "Requiere rol admin"},
        404: {"description": "Usuario no encontrado"},
        422: {"description": "No se puede degradar al último admin activo"}
    }
)
def cambiar_rol(
    id: int,
    datos: UsuarioActualizarRol,
    db: SessionDep,
    usuario_admin: UsuarioActualDep
):
    """
    Actualiza el rol de un usuario.
    Protege al último administrador activo y revoca los refresh tokens.
    """
    return usuario_controller.cambiar_rol(
        db=db,
        usuario_id=id,
        datos=datos,
        admin_autenticado=usuario_admin
    )


@router.patch(
    "/{id}/activo",
    response_model=UsuarioRespuesta,
    status_code=status.HTTP_200_OK,
    summary="Activar o desactivar usuario (Solo Admin)",
    responses={
        200: {"description": "Estado actualizado"},
        401: {"description": "No autenticado"},
        403: {"description": "Requiere rol admin"},
        404: {"description": "Usuario no encontrado"},
        422: {"description": "No se puede desactivar al último admin activo"}
    }
)
def cambiar_activo(
    id: int,
    datos: UsuarioActualizarActivo,
    db: SessionDep,
    usuario_admin: UsuarioActualDep
):
    """
    Activa o desactiva a un usuario.
    Protege al último administrador activo y revoca los tokens al desactivar.
    """
    return usuario_controller.cambiar_activo(
        db=db,
        usuario_id=id,
        datos=datos,
        admin_autenticado=usuario_admin
    )

