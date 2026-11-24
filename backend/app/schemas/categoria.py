from pydantic import BaseModel, ConfigDict, Field, field_validator


class CategoriaBase(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=50, description="Nombre de la categoría en minúsculas")
    descripcion: str | None = Field(default=None, max_length=200, description="Descripción de la categoría")

    @field_validator("nombre")
    @classmethod
    def validar_y_formatear_nombre(cls, v: str) -> str:
        limpio = v.strip().lower()
        if len(limpio) < 3 or len(limpio) > 50:
            raise ValueError("El nombre debe tener entre 3 y 50 caracteres")
        return limpio

    @field_validator("descripcion")
    @classmethod
    def validar_descripcion(cls, v: str | None) -> str | None:
        if v is not None:
            limpio = v.strip()
            return limpio if limpio else None
        return None


class CategoriaCrear(CategoriaBase):
    pass


class CategoriaActualizar(BaseModel):
    nombre: str | None = Field(default=None, min_length=3, max_length=50)
    descripcion: str | None = Field(default=None, max_length=200)

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, v: str | None) -> str | None:
        if v is not None:
            limpio = v.strip().lower()
            if len(limpio) < 3 or len(limpio) > 50:
                raise ValueError("El nombre debe tener entre 3 y 50 caracteres")
            return limpio
        return None

    @field_validator("descripcion")
    @classmethod
    def validar_descripcion(cls, v: str | None) -> str | None:
        if v is not None:
            limpio = v.strip()
            return limpio if limpio else None
        return None


class CategoriaRespuestaSimple(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str


class CategoriaRespuesta(CategoriaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
