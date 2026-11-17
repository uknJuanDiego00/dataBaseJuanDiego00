from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator
from datetime import datetime
from ..models.usuario import RolUsuario
from ..core.security import validar_complejidad_password


class RegistroSocio(BaseModel):
    nombre: str = Field(min_length=2, max_length=100, description="Nombre completo del socio")
    email: EmailStr = Field(description="Correo electrónico único")
    password: str = Field(min_length=8, max_length=64, description="Contraseña de acceso")
    password_confirmacion: str = Field(min_length=8, max_length=64, description="Confirmación de contraseña")
    telefono: str | None = Field(default=None, pattern=r"^[0-9+ ]{7,15}$", description="Teléfono de contacto")

    @field_validator("email")
    @classmethod
    def normalizar_email(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("nombre")
    @classmethod
    def formatear_nombre(cls, v: str) -> str:
        limpio = v.strip()
        if not limpio:
            raise ValueError("El nombre no puede estar vacío")
        return limpio.title()

    @field_validator("password")
    @classmethod
    def validar_password(cls, v: str) -> str:
        validar_complejidad_password(v)
        return v

    @model_validator(mode="after")
    def validar_contrasenas_iguales(self) -> "RegistroSocio":
        if self.password != self.password_confirmacion:
            raise ValueError("Las contraseñas no coinciden")
        return self


class TokenRespuesta(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="Segundos de validez del access token")


class RefreshTokenEntrada(BaseModel):
    refresh_token: str = Field(description="Token de refresco")


class CambiarPasswordEntrada(BaseModel):
    password_actual: str = Field(min_length=1, description="Contraseña actual")
    password_nueva: str = Field(min_length=8, max_length=64, description="Nueva contraseña")
    password_nueva_confirmacion: str = Field(min_length=8, max_length=64, description="Confirmación de nueva contraseña")

    @field_validator("password_nueva")
    @classmethod
    def validar_nueva_password(cls, v: str) -> str:
        validar_complejidad_password(v)
        return v

    @model_validator(mode="after")
    def validar_confirmacion(self) -> "CambiarPasswordEntrada":
        if self.password_nueva != self.password_nueva_confirmacion:
            raise ValueError("Las nuevas contraseñas no coinciden")
        return self


class AuthMeRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    nombre: str
    rol: RolUsuario
    activo: bool
    socio_id: int | None = None
    creado_en: datetime

