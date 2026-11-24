
from collections.abc import Generator
from typing import Annotated

import jwt
from fastapi import Depends, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .config import settings
from .database import SessionLocal
from .exceptions import NoAutenticado, Prohibido
from .security import decode_token
from ..models.usuario import RolUsuario, Usuario


# ============================================================
# 1. CONEXIÓN A BASE DE DATOS
# ============================================================

def get_db() -> Generator[Session, None, None]:
    """Proporciona una sesión de base de datos por petición."""

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


SessionDep = Annotated[Session, Depends(get_db)]


# ============================================================
# 2. PAGINACIÓN
# ============================================================

class Paginacion:
    """Parámetros reutilizables para paginar resultados."""

    def __init__(
        self,
        skip: int = Query(
            default=0,
            ge=0,
            description="Registros a omitir"
        ),
        limit: int = Query(
            default=10,
            ge=1,
            le=100,
            description="Límite de registros por página"
        )
    ):
        self.skip = skip
        self.limit = limit


PaginacionDep = Annotated[
    Paginacion,
    Depends(Paginacion)
]


# ============================================================
# 3. CONFIGURACIÓN OAUTH2
# ============================================================

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False
)


# ============================================================
# 4. OBTENER USUARIO AUTENTICADO
# ============================================================

def obtener_usuario_actual(
    token: Annotated[str | None, Depends(oauth2_scheme)],
    db: SessionDep
) -> Usuario:
    """
    Valida el token JWT y obtiene el usuario autenticado.

    Comprueba:
    - Existencia del token.
    - Validez y expiración.
    - Tipo de token.
    - Identificador del usuario.
    - Existencia del usuario.
    - Estado activo de la cuenta.
    """

    if not token:
        raise NoAutenticado(
            "Token de autenticación no proporcionado"
        )

    try:
        payload = decode_token(token)

    except jwt.ExpiredSignatureError:
        raise NoAutenticado("El token ha expirado")

    except jwt.InvalidTokenError:
        raise NoAutenticado("Token inválido")

    if payload.get("type") != "access":
        raise NoAutenticado("Tipo de token inválido")

    sub = payload.get("sub")

    if not sub:
        raise NoAutenticado(
            "Token inválido: claim sub ausente"
        )

    try:
        usuario_id = int(sub)

    except (ValueError, TypeError):
        raise NoAutenticado(
            "Token inválido: identificador incorrecto"
        )

    usuario = db.get(Usuario, usuario_id)

    if not usuario:
        raise NoAutenticado("Usuario no encontrado")

    if not usuario.activo:
        raise NoAutenticado("Usuario inactivo")

    return usuario


# Alias reutilizable para obtener el usuario autenticado.
UsuarioActualDep = Annotated[
    Usuario,
    Depends(obtener_usuario_actual)
]


# ============================================================
# 5. OBTENER USUARIO OPCIONAL
# ============================================================

def obtener_usuario_opcional(
    token: Annotated[str | None, Depends(oauth2_scheme)],
    db: SessionDep
) -> Usuario | None:
    """
    Obtiene el usuario si existe un token válido.

    Si no hay token o no es válido, retorna None.
    """

    if not token:
        return None

    try:
        return obtener_usuario_actual(
            token=token,
            db=db
        )

    except NoAutenticado:
        return None


UsuarioOpcionalDep = Annotated[
    Usuario | None,
    Depends(obtener_usuario_opcional)
]


# ============================================================
# 6. AUTORIZACIÓN BASADA EN ROLES (RBAC)
# ============================================================

def requiere_rol(*roles_permitidos: RolUsuario | str):
    """
    Verifica que el usuario autenticado tenga uno de
    los roles autorizados.

    Ejemplo:
        Depends(requiere_rol(RolUsuario.admin))
    """

    roles_str = {
        rol.value if isinstance(rol, RolUsuario) else str(rol)
        for rol in roles_permitidos
    }

    def verificar_rol(
        usuario: UsuarioActualDep
    ) -> Usuario:
        """Comprueba el rol del usuario autenticado."""

        rol_usuario = (
            usuario.rol.value
            if isinstance(usuario.rol, RolUsuario)
            else str(usuario.rol)
        )

        if rol_usuario not in roles_str:
            raise Prohibido(
                "No tiene permisos para realizar esta acción"
            )

        return usuario

    return verificar_rol
