from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordRequestForm
import jwt
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.exceptions import Conflicto, CuentaBloqueada, NoAutenticado, ReglaNegocio
from ..core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password
)
from ..models.refresh_token import RefreshToken
from ..models.socio import Socio
from ..models.usuario import RolUsuario, Usuario
from ..schemas.auth import CambiarPasswordEntrada, RegistroSocio, TokenRespuesta


def login(db: Session, form_data: OAuth2PasswordRequestForm) -> TokenRespuesta:
    """
    Autentica al usuario usando OAuth2 Password Flow.
    Controla bloqueo por 5 intentos fallidos consecutivos durante 15 minutos (HTTP 423).
    Mensaje uniforme para credenciales incorrectas.
    """
    email_limpio = form_data.username.strip().lower()
    ahora = datetime.now(timezone.utc)

    usuario = db.scalar(
        select(Usuario).where(func.lower(Usuario.email) == email_limpio)
    )

    # Verificar si la cuenta está bloqueada
    if usuario and usuario.bloqueado_hasta:
        if usuario.bloqueado_hasta > ahora:
            raise CuentaBloqueada("Cuenta bloqueada temporalmente. Intente más tarde.")
        else:
            # El tiempo de bloqueo ya expiró
            usuario.bloqueado_hasta = None
            usuario.intentos_fallidos = 0
            db.commit()

    # Validar credenciales
    if not usuario or not verify_password(form_data.password, usuario.password_hash):
        if usuario:
            usuario.intentos_fallidos += 1
            if usuario.intentos_fallidos >= 5:
                usuario.bloqueado_hasta = ahora + timedelta(minutes=15)
                db.commit()
                raise CuentaBloqueada("Cuenta bloqueada temporalmente por 5 intentos fallidos.")
            db.commit()
        # Mensaje uniforme para no revelar si el usuario existe o no
        raise NoAutenticado("Credenciales incorrectas")

    if not usuario.activo:
        raise NoAutenticado("Usuario inactivo")

    # Login exitoso: reiniciar contador de fallos
    usuario.intentos_fallidos = 0
    usuario.bloqueado_hasta = None

    rol_str = usuario.rol.value if isinstance(usuario.rol, RolUsuario) else str(usuario.rol)
    access_token = create_access_token(usuario.id, rol_str)
    refresh_token_jwt, jti, exp = create_refresh_token(usuario.id, rol_str)

    # Persistir refresh token
    token_db = RefreshToken(
        jti=jti,
        usuario_id=usuario.id,
        expira_en=exp,
        revocado=False
    )
    db.add(token_db)
    db.commit()

    return TokenRespuesta(
        access_token=access_token,
        refresh_token=refresh_token_jwt,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


def refresh(db: Session, token_str: str) -> TokenRespuesta:
    """
    Valida y rota un refresh token.
    Si se detecta reutilización de un token revocado, invalida TODOS los refresh tokens del usuario.
    """
    try:
        payload = decode_token(token_str)
    except jwt.ExpiredSignatureError:
        raise NoAutenticado("Refresh token expirado")
    except Exception:
        raise NoAutenticado("Refresh token inválido")

    if payload.get("type") != "refresh":
        raise NoAutenticado("Tipo de token inválido")

    jti = payload.get("jti")
    sub = payload.get("sub")
    if not jti or not sub:
        raise NoAutenticado("Token incompleto")

    usuario_id = int(sub)
    token_record = db.scalar(
        select(RefreshToken).where(RefreshToken.jti == jti)
    )

    if not token_record:
        raise NoAutenticado("Refresh token no encontrado")

    # Detección de reutilización de token revocado
    if token_record.revocado:
        # Revocación masiva por sospecha de compromiso
        db.execute(
            update(RefreshToken)
            .where(RefreshToken.usuario_id == usuario_id)
            .values(revocado=True)
        )
        db.commit()
        raise NoAutenticado("Refresh token revocado previamente. Todos los tokens han sido invalidados.")

    ahora = datetime.now(timezone.utc)
    # Validar zona horaria en expira_en
    expira_en = token_record.expira_en
    if expira_en.tzinfo is None:
        expira_en = expira_en.replace(tzinfo=timezone.utc)

    if expira_en < ahora:
        raise NoAutenticado("Refresh token expirado")

    # Revocar el token utilizado (rotación)
    token_record.revocado = True

    usuario = db.get(Usuario, usuario_id)
    if not usuario or not usuario.activo:
        db.commit()
        raise NoAutenticado("Usuario no válido o inactivo")

    rol_str = usuario.rol.value if isinstance(usuario.rol, RolUsuario) else str(usuario.rol)
    nuevo_access = create_access_token(usuario.id, rol_str)
    nuevo_refresh, nuevo_jti, nuevo_exp = create_refresh_token(usuario.id, rol_str)

    nuevo_token_db = RefreshToken(
        jti=nuevo_jti,
        usuario_id=usuario.id,
        expira_en=nuevo_exp,
        revocado=False
    )
    db.add(nuevo_token_db)
    db.commit()

    return TokenRespuesta(
        access_token=nuevo_access,
        refresh_token=nuevo_refresh,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


def logout(db: Session, token_str: str) -> None:
    """Revoca el refresh token especificado."""
    try:
        payload = decode_token(token_str)
        jti = payload.get("jti")
        if jti:
            token_record = db.scalar(
                select(RefreshToken).where(RefreshToken.jti == jti)
            )
            if token_record:
                token_record.revocado = True
                db.commit()
    except Exception:
        # Si el token no es decodificable, no se interrumpe el logout
        pass


def registrar_socio(db: Session, datos: RegistroSocio) -> Usuario:
    """
    Registra públicamente a un nuevo socio creando la cuenta de Usuario
    y la ficha de Socio en una sola transacción atómica.
    """
    email_norm = datos.email.strip().lower()

    # Comprobar unicidad en Usuario y Socio
    usuario_existente = db.scalar(
        select(Usuario).where(func.lower(Usuario.email) == email_norm)
    )
    socio_existente = db.scalar(
        select(Socio).where(func.lower(Socio.email) == email_norm)
    )
    if usuario_existente or socio_existente:
        raise Conflicto("El correo electrónico ya se encuentra registrado")

    # Crear Socio
    socio = Socio(
        nombre=datos.nombre,
        email=email_norm,
        telefono=datos.telefono,
        activo=True
    )
    db.add(socio)
    db.flush()

    # Crear Usuario enlazado
    usuario = Usuario(
        email=email_norm,
        nombre=datos.nombre,
        password_hash=get_password_hash(datos.password),
        rol=RolUsuario.socio,
        activo=True,
        socio_id=socio.id
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    return usuario


def cambiar_password(db: Session, usuario: Usuario, datos: CambiarPasswordEntrada) -> None:
    """
    Cambia la contraseña del usuario autenticado y revoca todos sus refresh tokens.
    """
    if not verify_password(datos.password_actual, usuario.password_hash):
        raise ReglaNegocio("La contraseña actual no es correcta")

    usuario.password_hash = get_password_hash(datos.password_nueva)

    # Revocar todos los refresh tokens del usuario
    db.execute(
        update(RefreshToken)
        .where(RefreshToken.usuario_id == usuario.id)
        .values(revocado=True)
    )
    db.commit()

