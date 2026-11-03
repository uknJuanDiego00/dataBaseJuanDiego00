from collections.abc import Generator
from typing import Annotated
from fastapi import Depends, Query
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.orm import Session

from .config import settings
from .database import SessionLocal
from .exceptions import NoAutenticado, Prohibido
from .security import decode_token
from ..models.usuario import RolUsuario, Usuario


# Proveedor de sesión de base de datos
def get_db() -> Generator[Session, None, None]:
    """Generador que provee una sesión de base de datos por petición."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


SessionDep = Annotated[Session, Depends(get_db)]


class Paginacion:
    """Parámetros reutilizables de paginación."""
    def __init__(
        self,
        skip: int = Query(default=0, ge=0, description="Registros a omitir"),
        limit: int = Query(default=10, ge=1, le=100, description="Límite de registros por página (máx. 100)")
    ):
        self.skip = skip
        self.limit = limit


PaginacionDep = Annotated[Paginacion, Depends(Paginacion)]


# ------------------------------------------------------------------
# OAuth2 y Autenticación de Usuario
# ------------------------------------------------------------------
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False
)


def obtener_usuario_actual(
    token: Annotated[str | None, Depends(oauth2_scheme)],
    db: SessionDep
) -> Usuario:
    """
    Extrae, valida y autentica el usuario actual a partir del Bearer token JWT.
    Lanza 401 si no hay token, el token es inválido, expiró o no es de tipo 'access'.
    """
    if not token:
        raise NoAutenticado("Token de autenticación no proporcionado")

    try:
        payload = decode_token(token)
    except jwt.ExpiredSignatureError:
        raise NoAutenticado("El token ha expirado")
    except (jwt.InvalidTokenError, Exception):
        raise NoAutenticado("Token inválido")

    # Validar que sea un access token
    if payload.get("type") != "access":
        raise NoAutenticado("Tipo de token inválido")

    sub = payload.get("sub")
    if not sub:
        raise NoAutenticado("Token inválido (claim sub ausente)")

    try:
        usuario_id = int(sub)
    except ValueError:
        raise NoAutenticado("Token inválido (sub inválido)")

    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise NoAutenticado("Usuario no encontrado")

    if not usuario.activo:
        raise NoAutenticado("Usuario inactivo")

    return usuario


UsuarioActualDep = Annotated[Usuario, Depends(obtener_usuario_actual)]


def obtener_usuario_opcional(
    token: Annotated[str | None, Depends(oauth2_scheme)],
    db: SessionDep
) -> Usuario | None:
    """Retorna el usuario si el token es válido, o None si no se envió token."""
    if not token:
        return None
    try:
        return obtener_usuario_actual(token=token, db=db)
    except NoAutenticado:
        return None


UsuarioOpcionalDep = Annotated[Usuario | None, Depends(obtener_usuario_opcional)]


# ------------------------------------------------------------------
# Dependencia de Autorización: requiere_rol
# ------------------------------------------------------------------
def requiere_rol(*roles_permitidos: RolUsuario | str):
    """
    Dependencia de autorización basada en roles (RBAC).
    Verifica que el usuario autenticado tenga uno de los roles permitidos.
    Lanza 403 Prohibido si no tiene los permisos suficientes.
    """
    roles_str = {
        r.value if isinstance(r, RolUsuario) else str(r)
        for r in roles_permitidos
    }

    def _verificar_rol(usuario: UsuarioActualDep) -> Usuario:
        rol_usuario = usuario.rol.value if isinstance(usuario.rol, RolUsuario) else str(usuario.rol)
        if rol_usuario not in roles_str:
            raise Prohibido("No tiene permisos para realizar esta acción")
        return usuario

    return _verificar_rol
