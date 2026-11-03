from fastapi import APIRouter, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..controllers import auth_controller
from ..core.dependencies import SessionDep, UsuarioActualDep
from ..schemas.auth import (
    AuthMeRespuesta,
    CambiarPasswordEntrada,
    RefreshTokenEntrada,
    RegistroSocio,
    TokenRespuesta
)
from ..schemas.usuario import UsuarioRespuesta

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Autenticación"]
)


@router.post(
    "/registro",
    response_model=UsuarioRespuesta,
    status_code=status.HTTP_201_CREATED,
    summary="Registro público de socios",
    responses={
        201: {"description": "Usuario y socio creados exitosamente"},
        400: {"description": "Datos de entrada inválidos"},
        409: {"description": "Correo ya registrado"},
        429: {"description": "Límite de peticiones excedido (máx. 5/min)"}
    }
)
@limiter.limit("5/minute")
def registrar_socio(request: Request, datos: RegistroSocio, db: SessionDep):
    """
    Registro público para nuevos socios.
    Crea el usuario y la ficha de socio en una sola transacción atómica.
    """
    return auth_controller.registrar_socio(db=db, datos=datos)


@router.post(
    "/login",
    response_model=TokenRespuesta,
    status_code=status.HTTP_200_OK,
    summary="Inicio de sesión (OAuth2 Password Flow)",
    responses={
        200: {"description": "Tokens emitidos exitosamente"},
        401: {"description": "Credenciales inválidas"},
        423: {"description": "Cuenta bloqueada temporalmente"},
        429: {"description": "Límite de peticiones excedido (máx. 10/min)"}
    }
)
@limiter.limit("10/minute")
def login(request: Request, db: SessionDep, form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Autentica un usuario mediante su correo (username) y contraseña.
    Devuelve un access token y un refresh token.
    Bloquea la cuenta por 15 minutos tras 5 intentos fallidos consecutivos.
    """
    return auth_controller.login(db=db, form_data=form_data)


@router.post(
    "/refresh",
    response_model=TokenRespuesta,
    status_code=status.HTTP_200_OK,
    summary="Rotación y renovación de tokens",
    responses={
        200: {"description": "Nuevos tokens emitidos exitosamente"},
        401: {"description": "Refresh token expirado, inválido o revocado"}
    }
)
def refresh_token(datos: RefreshTokenEntrada, db: SessionDep):
    """
    Recibe un refresh token válido, lo revoca e issue un nuevo par de tokens (rotación).
    Si se detecta reutilización de un token ya rotado, se revocan todos los tokens del usuario.
    """
    return auth_controller.refresh(db=db, token_str=datos.refresh_token)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cierre de sesión y revocación de token",
    responses={
        204: {"description": "Sesión cerrada correctamente"}
    }
)
def logout(datos: RefreshTokenEntrada, db: SessionDep):
    """
    Cierra la sesión del usuario revocando el refresh token enviado.
    """
    auth_controller.logout(db=db, token_str=datos.refresh_token)
    return None


@router.get(
    "/me",
    response_model=AuthMeRespuesta,
    status_code=status.HTTP_200_OK,
    summary="Consultar datos del usuario autenticado",
    responses={
        200: {"description": "Datos del perfil autenticado"},
        401: {"description": "No autenticado"}
    }
)
def obtener_perfil(usuario: UsuarioActualDep):
    """
    Retorna la información del usuario actualmente autenticado a partir del JWT.
    """
    return usuario


@router.patch(
    "/me/password",
    status_code=status.HTTP_200_OK,
    summary="Cambio de contraseña del usuario autenticado",
    responses={
        200: {"description": "Contraseña actualizada exitosamente"},
        400: {"description": "Contraseña nueva inválida o no coincide"},
        401: {"description": "No autenticado"},
        422: {"description": "Contraseña actual incorrecta"}
    }
)
def cambiar_password(
    datos: CambiarPasswordEntrada,
    usuario: UsuarioActualDep,
    db: SessionDep
):
    """
    Permite al usuario autenticado cambiar su contraseña tras validar la actual.
    Revoca todos sus refresh tokens activos tras el cambio exitoso.
    """
    auth_controller.cambiar_password(db=db, usuario=usuario, datos=datos)
    return {"mensaje": "Contraseña actualizada exitosamente"}

