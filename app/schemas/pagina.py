from typing import Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class Pagina(BaseModel, Generic[T]):
    """Esquema genérico para respuestas paginadas estándar."""
    items: list[T] = Field(description="Lista de elementos de la página actual")
    total: int = Field(ge=0, description="Cantidad total de registros encontrados")
    skip: int = Field(ge=0, description="Cantidad de registros omitidos")
    limit: int = Field(ge=1, description="Límite máximo de registros solicitados por página")

