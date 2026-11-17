from datetime import datetime, timedelta, timezone
import re
import uuid
import jwt
from pwdlib import PasswordHash
from .config import settings

# ------------------------------------------------------------------
# Hasher de contraseñas Argon2 mediante pwdlib
# ------------------------------------------------------------------
password_hasher = PasswordHash.recommended()


def get_password_hash(password: str) -> str:
    """Genera el hash Argon2 de una contraseña en texto plano."""
    return password_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si una contraseña en texto plano coincide con su hash Argon2."""
    return password_hasher.verify(plain_password, hashed_password)


def validar_complejidad_password(password: str) -> None:
    """
    Valida las reglas de complejidad para contraseñas:
    - Longitud entre 8 y 64 caracteres.
    - Al menos una letra mayúscula.
    - Al menos una letra minúscula.
    - Al menos un dígito numérico.
    """
    if len(password) < 8 or len(password) > 64:
        raise ValueError("La contraseña debe tener entre 8 y 64 caracteres")
    if not re.search(r"[A-Z]", password):
        raise ValueError("La contraseña debe incluir al menos una letra mayúscula")
    if not re.search(r"[a-z]", password):
        raise ValueError("La contraseña debe incluir al menos una letra minúscula")
    if not re.search(r"[0-9]", password):
        raise ValueError("La contraseña debe incluir al menos un número")


# ------------------------------------------------------------------
# Generación y Validación de Tokens JWT (PyJWT)
# ------------------------------------------------------------------
def create_access_token(usuario_id: int, rol: str) -> str:
    """
    Genera un access token JWT con claims:
    sub, rol, type, iat, exp, jti.
    """
    ahora = datetime.now(timezone.utc)
    exp = ahora + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    jti = str(uuid.uuid4())

    payload = {
        "sub": str(usuario_id),
        "rol": rol,
        "type": "access",
        "iat": int(ahora.timestamp()),
        "exp": int(exp.timestamp()),
        "jti": jti,
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(
    usuario_id: int,
    rol: str,
    jti: str | None = None
) -> tuple[str, str, datetime]:
    """
    Genera un refresh token JWT con claims:
    sub, rol, type, iat, exp, jti.
    Retorna (token_jwt, jti, fecha_expiracion).
    """
    ahora = datetime.now(timezone.utc)
    exp = ahora + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    token_jti = jti or str(uuid.uuid4())

    payload = {
        "sub": str(usuario_id),
        "rol": rol,
        "type": "refresh",
        "iat": int(ahora.timestamp()),
        "exp": int(exp.timestamp()),
        "jti": token_jti,
    }

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token, token_jti, exp


def decode_token(token: str) -> dict:
    """
    Decodifica y valida un token JWT utilizando exclusivamente el algoritmo configurado.
    Lanza excepciones de PyJWT si el token está expirado, es inválido o tiene algoritmo alterado.
    """
    return jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM]
    )

