from fastapi import APIRouter, Depends, Query, status
from ..controllers import socio_controller
from ..core.dependencies import PaginacionDep, SessionDep, UsuarioActualDep, requiere_rol
from ..core.exceptions import NoEncontrado, Prohibido
from ..models.usuario import RolUsuario
from ..schemas.pagina import Pagina
from ..schemas.prestamo import EstadoPrestamoEnum, PrestamoRespuesta
from ..schemas.socio import (
    SocioActualizar,
    SocioCrear,
    SocioMeActualizar,
    SocioRespuesta
)

router = APIRouter(
    prefix="/socios",
    tags=["Socios"]
)


# ------------------------------------------------------------------
# Endpoints contextuales para el socio autenticado (/socios/me)
# ------------------------------------------------------------------
@router.get(
    "/me",
    response_model=SocioRespuesta,
    status_code=status.HTTP_200_OK,
    summary="Consultar ficha de socio del usuario autenticado",
    responses={
        200: {"description": "Datos del socio autenticado"},
        401: {"description": "No autenticado"},
        404: {"description": "El usuario no tiene una ficha de socio asociada"}
    }
)
def obtener_mi_perfil_socio(usuario: UsuarioActualDep, db: SessionDep):
    """Retorna los datos del socio vinculado al usuario en sesión."""
    if not usuario.socio_id:
        raise NoEncontrado("No existe ficha de socio asociada a este usuario")
    return socio_controller.obtener_socio(db=db, socio_id=usuario.socio_id)


@router.patch(
    "/me",
    response_model=SocioRespuesta,
    status_code=status.HTTP_200_OK,
    summary="Actualizar perfil propio del socio",
    responses={
        200: {"description": "Perfil actualizado"},
        401: {"description": "No autenticado"},
        404: {"description": "Ficha de socio no encontrada"}
    }
)
def actualizar_mi_perfil_socio(
    datos: SocioMeActualizar,
    usuario: UsuarioActualDep,
    db: SessionDep
):
    """
    Permite al socio actualizar sus datos personales (nombre y teléfono).
    Regla Z4: No puede modificar email, rol ni activo.
    """
    if not usuario.socio_id:
        raise NoEncontrado("No existe ficha de socio asociada a este usuario")
    return socio_controller.actualizar_socio_me(
        db=db,
        socio_id=usuario.socio_id,
        datos=datos
    )


@router.get(
    "/me/prestamos",
    response_model=Pagina[PrestamoRespuesta],
    status_code=status.HTTP_200_OK,
    summary="Consultar préstamos propios del socio autenticado",
    responses={
        200: {"description": "Página con préstamos del socio"},
        401: {"description": "No autenticado"},
        404: {"description": "Ficha de socio no encontrada"}
    }
)
def listar_mis_prestamos(
    usuario: UsuarioActualDep,
    db: SessionDep,
    paginacion: PaginacionDep,
    estado: EstadoPrestamoEnum | None = Query(default=None, description="Filtrar por estado")
):
    """Retorna los préstamos del socio autenticado."""
    if not usuario.socio_id:
        raise NoEncontrado("No existe ficha de socio asociada a este usuario")
    return socio_controller.listar_prestamos_socio(
        db=db,
        socio_id=usuario.socio_id,
        skip=paginacion.skip,
        limit=paginacion.limit,
        estado=estado
    )


@router.get(
    "/me/multas",
    response_model=Pagina[PrestamoRespuesta],
    status_code=status.HTTP_200_OK,
    summary="Consultar multas propias del socio autenticado",
    responses={
        200: {"description": "Préstamos con multas del socio"},
        401: {"description": "No autenticado"},
        404: {"description": "Ficha de socio no encontrada"}
    }
)
def listar_mis_multas(
    usuario: UsuarioActualDep,
    db: SessionDep,
    paginacion: PaginacionDep
):
    """Retorna los préstamos con multas aplicadas al socio autenticado."""
    if not usuario.socio_id:
        raise NoEncontrado("No existe ficha de socio asociada a este usuario")
    return socio_controller.listar_multas_socio(
        db=db,
        socio_id=usuario.socio_id,
        skip=paginacion.skip,
        limit=paginacion.limit
    )


# ------------------------------------------------------------------
# Endpoints de administración de socios
# ------------------------------------------------------------------
@router.get(
    "",
    response_model=Pagina[SocioRespuesta],
    status_code=status.HTTP_200_OK,
    summary="Listar socios paginados (Bibliotecario o Admin)",
    responses={
        200: {"description": "Página de socios"},
        401: {"description": "No autenticado"},
        403: {"description": "Requiere rol bibliotecario o admin"}
    }
)
def listar_socios(
    db: SessionDep,
    paginacion: PaginacionDep,
    usuario: UsuarioActualDep = Depends(requiere_rol(RolUsuario.bibliotecario, RolUsuario.admin)),
    activo: bool | None = Query(default=None, description="Filtrar por estado activo/inactivo")
):
    """Lista paginada de socios con filtro opcional por estado."""
    return socio_controller.listar_socios(
        db=db,
        skip=paginacion.skip,
        limit=paginacion.limit,
        activo=activo
    )


@router.get(
    "/{id}",
    response_model=SocioRespuesta,
    status_code=status.HTTP_200_OK,
    summary="Consultar un socio por su ID",
    responses={
        200: {"description": "Detalle del socio"},
        401: {"description": "No autenticado"},
        403: {"description": "No autorizado para consultar este socio"},
        404: {"description": "Socio no encontrado"}
    }
)
def obtener_socio(id: int, db: SessionDep, usuario: UsuarioActualDep):
    """Consulta un socio por su ID. Los socios solo pueden consultar su propia ficha."""
    if usuario.rol == RolUsuario.socio and usuario.socio_id != id:
        raise Prohibido("No tiene permisos para consultar información de otros socios")
    return socio_controller.obtener_socio(db=db, socio_id=id)


@router.post(
    "",
    response_model=SocioRespuesta,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un socio (Bibliotecario o Admin)",
    responses={
        201: {"description": "Socio creado exitosamente"},
        401: {"description": "No autenticado"},
        403: {"description": "Requiere rol bibliotecario o admin"},
        409: {"description": "Correo ya registrado"}
    }
)
def crear_socio(
    datos: SocioCrear,
    db: SessionDep,
    usuario: UsuarioActualDep = Depends(requiere_rol(RolUsuario.bibliotecario, RolUsuario.admin))
):
    """Crea un nuevo socio en el sistema."""
    return socio_controller.crear_socio(db=db, datos=datos)


@router.patch(
    "/{id}",
    response_model=SocioRespuesta,
    status_code=status.HTTP_200_OK,
    summary="Actualizar datos de un socio (Bibliotecario o Admin)",
    responses={
        200: {"description": "Socio actualizado"},
        401: {"description": "No autenticado"},
        403: {"description": "Requiere rol bibliotecario o admin"},
        404: {"description": "Socio no encontrado"},
        409: {"description": "Correo duplicado"}
    }
)
def actualizar_socio(
    id: int,
    datos: SocioActualizar,
    db: SessionDep,
    usuario: UsuarioActualDep = Depends(requiere_rol(RolUsuario.bibliotecario, RolUsuario.admin))
):
    """Actualiza los datos de un socio."""
    return socio_controller.actualizar_socio(db=db, socio_id=id, datos=datos)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar o desactivar un socio (Solo Admin)",
    responses={
        204: {"description": "Socio eliminado o desactivado"},
        401: {"description": "No autenticado"},
        403: {"description": "Requiere rol admin"},
        404: {"description": "Socio no encontrado"},
        409: {"description": "Tiene préstamos activos sin devolver"}
    }
)
def eliminar_socio(
    id: int,
    db: SessionDep,
    usuario: UsuarioActualDep = Depends(requiere_rol(RolUsuario.admin))
):
    """
    Elimina o desactiva un socio:
    - 409 si tiene préstamos activos sin devolver.
    - Se desactiva si tiene préstamos devueltos en historial.
    - Se borra físicamente si no tiene préstamos.
    """
    socio_controller.eliminar_socio(db=db, socio_id=id)
    return None


@router.get(
    "/{id}/prestamos",
    response_model=Pagina[PrestamoRespuesta],
    status_code=status.HTTP_200_OK,
    summary="Listar préstamos de un socio por ID",
    responses={
        200: {"description": "Página de préstamos del socio"},
        401: {"description": "No autenticado"},
        403: {"description": "No autorizado para consultar los préstamos de este socio"},
        404: {"description": "Socio no encontrado"}
    }
)
def listar_prestamos_socio(
    id: int,
    db: SessionDep,
    paginacion: PaginacionDep,
    usuario: UsuarioActualDep,
    estado: EstadoPrestamoEnum | None = Query(default=None, description="Filtrar por estado")
):
    """Lista los préstamos de un socio específico. Los socios solo pueden consultar los suyos."""
    if usuario.rol == RolUsuario.socio and usuario.socio_id != id:
        raise Prohibido("No tiene permisos para consultar préstamos de otros socios")
    return socio_controller.listar_prestamos_socio(
        db=db,
        socio_id=id,
        skip=paginacion.skip,
        limit=paginacion.limit,
        estado=estado
    )
