from datetime import date
from pydantic import BaseModel, ConfigDict, Field, field_validator


class AutorBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100, description="Nombre del autor en formato título")
    nacionalidad: str | None = Field(default=None, max_length=60, description="Nacionalidad del autor")
    anio_nacimiento: int | None = Field(default=None, ge=1000, description="Año de nacimiento (1000 - año actual)")

    @field_validator("nombre")
    @classmethod
    def validar_y_formatear_nombre(cls, v: str) -> str:
        limpio = v.strip()
        if len(limpio) < 2 or len(limpio) > 100:
            raise ValueError("El nombre debe tener entre 2 y 100 caracteres")
        return limpio.title()

    @field_validator("nacionalidad")
    @classmethod
    def validar_nacionalidad(cls, v: str | None) -> str | None:
        if v is not None:
            limpio = v.strip()
            return limpio if limpio else None
        return None

    @field_validator("anio_nacimiento")
    @classmethod
    def validar_anio_nacimiento(cls, v: int | None) -> int | None:
        if v is not None:
            anio_actual = date.today().year
            if v > anio_actual:
                raise ValueError(f"El año de nacimiento no puede ser mayor al año actual ({anio_actual})")
        return v


class AutorCrear(AutorBase):
    pass


class AutorActualizar(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=100)
    nacionalidad: str | None = Field(default=None, max_length=60)
    anio_nacimiento: int | None = Field(default=None, ge=1000)

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, v: str | None) -> str | None:
        if v is not None:
            limpio = v.strip()
            if len(limpio) < 2 or len(limpio) > 100:
                raise ValueError("El nombre debe tener entre 2 y 100 caracteres")
            return limpio.title()
        return None

    @field_validator("nacionalidad")
    @classmethod
    def validar_nacionalidad(cls, v: str | None) -> str | None:
        if v is not None:
            limpio = v.strip()
            return limpio if limpio else None
        return None

    @field_validator("anio_nacimiento")
    @classmethod
    def validar_anio_nacimiento(cls, v: int | None) -> int | None:
        if v is not None:
            anio_actual = date.today().year
            if v > anio_actual:
                raise ValueError(f"El año de nacimiento no puede ser mayor al año actual ({anio_actual})")
        return v


class AutorRespuestaSimple(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str


class AutorRespuesta(AutorBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
