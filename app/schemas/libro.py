from datetime import date
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, field_validator
from .autor import AutorRespuestaSimple
from .categoria import CategoriaRespuestaSimple


class OrdenLibrosEnum(str, Enum):
    titulo = "titulo"
    anio = "anio"
    menos_anio = "-anio"


class LibroBase(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=150, description="Título del libro")
    isbn: str = Field(..., pattern=r"^\d{13}$", description="Código ISBN de exactamente 13 dígitos")
    anio_publicacion: int = Field(..., ge=1450, description="Año de publicación (1450 - año actual)")
    ejemplares: int = Field(..., ge=1, le=50, description="Copias disponibles en la biblioteca (1 - 50)")
    autor_id: int = Field(..., gt=0, description="Identificador del autor")

    @field_validator("titulo")
    @classmethod
    def validar_y_formatear_titulo(cls, v: str) -> str:
        limpio = v.strip()
        if not limpio:
            raise ValueError("El título no puede estar vacío")
        return limpio.title()

    @field_validator("anio_publicacion")
    @classmethod
    def validar_anio_publicacion(cls, v: int) -> int:
        anio_actual = date.today().year
        if v > anio_actual:
            raise ValueError(f"El año de publicación no puede superar el año actual ({anio_actual})")
        return v


class LibroCrear(LibroBase):
    categoria_ids: list[int] = Field(
        ...,
        min_length=1,
        max_length=5,
        description="Lista de IDs de categorías (entre 1 y 5, sin duplicados)"
    )

    @field_validator("categoria_ids")
    @classmethod
    def validar_categoria_ids(cls, v: list[int]) -> list[int]:
        if len(v) != len(set(v)):
            raise ValueError("Las categorías no pueden contener duplicados")
        return v


class LibroActualizar(BaseModel):
    titulo: str | None = Field(default=None, min_length=1, max_length=150)
    isbn: str | None = Field(default=None, pattern=r"^\d{13}$")
    anio_publicacion: int | None = Field(default=None, ge=1450)
    ejemplares: int | None = Field(default=None, ge=0, le=50)
    autor_id: int | None = Field(default=None, gt=0)
    categoria_ids: list[int] | None = Field(default=None, min_length=1, max_length=5)

    @field_validator("titulo")
    @classmethod
    def validar_titulo(cls, v: str | None) -> str | None:
        if v is not None:
            limpio = v.strip()
            if not limpio:
                raise ValueError("El título no puede estar vacío")
            return limpio.title()
        return None

    @field_validator("anio_publicacion")
    @classmethod
    def validar_anio(cls, v: int | None) -> int | None:
        if v is not None:
            anio_actual = date.today().year
            if v > anio_actual:
                raise ValueError(f"El año de publicación no puede superar el año actual ({anio_actual})")
        return v

    @field_validator("categoria_ids")
    @classmethod
    def validar_categoria_ids(cls, v: list[int] | None) -> list[int] | None:
        if v is not None:
            if len(v) != len(set(v)):
                raise ValueError("Las categorías no pueden contener duplicados")
        return v


class LibroRespuestaSimple(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    titulo: str
    isbn: str


class LibroRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    titulo: str
    isbn: str
    anio_publicacion: int
    ejemplares: int
    autor_id: int
    disponibles: int
    autor: AutorRespuestaSimple
    categorias: list[CategoriaRespuestaSimple]
