from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class SocioBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100, description="Nombre completo en formato título")
    email: EmailStr = Field(..., description="Correo electrónico único del socio")
    telefono: str | None = Field(
        default=None,
        pattern=r"^[0-9+ ]{7,15}$",
        description="Teléfono opcional (7 a 15 caracteres: dígitos, espacios o +)"
    )
    activo: bool = Field(default=True, description="Estado del socio en la biblioteca")

    @field_validator("nombre")
    @classmethod
    def validar_y_formatear_nombre(cls, v: str) -> str:
        limpio = v.strip()
        if not limpio:
            raise ValueError("El nombre no puede estar vacío")
        return limpio.title()

    @field_validator("email")
    @classmethod
    def validar_email(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("telefono")
    @classmethod
    def validar_telefono(cls, v: str | None) -> str | None:
        if v is not None:
            limpio = v.strip()
            return limpio if limpio else None
        return None


class SocioCrear(SocioBase):
    pass


class SocioActualizar(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=100)
    email: EmailStr | None = None
    telefono: str | None = Field(default=None, pattern=r"^[0-9+ ]{7,15}$")
    activo: bool | None = None

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, v: str | None) -> str | None:
        if v is not None:
            limpio = v.strip()
            if not limpio:
                raise ValueError("El nombre no puede estar vacío")
            return limpio.title()
        return None

    @field_validator("email")
    @classmethod
    def validar_email(cls, v: str | None) -> str | None:
        if v is not None:
            return v.strip().lower()
        return None

    @field_validator("telefono")
    @classmethod
    def validar_telefono(cls, v: str | None) -> str | None:
        if v is not None:
            limpio = v.strip()
            return limpio if limpio else None
        return None


class SocioRespuestaSimple(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    email: str


class SocioRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    email: str
    telefono: str | None = None
    activo: bool
    fecha_alta: datetime
