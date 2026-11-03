from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator
from ..models.usuario import RolUsuario
from ..core.security import validar_complejidad_password


class UsuarioBase(BaseModel):
    email: EmailStr = Field(description="Correo electrónico único del usuario")
    nombre: str = Field(min_length=2, max_length=100, description="Nombre completo")

    @field_validator("email")
    @classmethod
    def normalizar_email(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, v: str) -> str:
        limpio = v.strip()
        if not limpio:
            raise ValueError("El nombre no puede estar vacío")
        return limpio.title()


class UsuarioCrear(UsuarioBase):
    password: str = Field(min_length=8, max_length=64, description="Contraseña")
    password_confirmacion: str = Field(min_length=8, max_length=64, description="Confirmación de contraseña")
    rol: RolUsuario = Field(default=RolUsuario.socio, description="Rol del usuario en el sistema")

    @field_validator("password")
    @classmethod
    def validar_password(cls, v: str) -> str:
        validar_complejidad_password(v)
        return v

    @model_validator(mode="after")
    def validar_confirmacion(self) -> "UsuarioCrear":
        if self.password != self.password_confirmacion:
            raise ValueError("Las contraseñas no coinciden")
        return self


class UsuarioActualizarRol(BaseModel):
    rol: RolUsuario = Field(description="Nuevo rol para el usuario")


class UsuarioActualizarActivo(BaseModel):
    activo: bool = Field(description="Nuevo estado de activación para el usuario")


class UsuarioRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    nombre: str
    rol: RolUsuario
    activo: bool
    socio_id: int | None = None
    creado_en: datetime

