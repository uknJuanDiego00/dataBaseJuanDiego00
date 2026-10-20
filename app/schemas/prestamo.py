from datetime import date
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, field_validator
from .libro import LibroRespuestaSimple
from .socio import SocioRespuestaSimple


class EstadoPrestamoEnum(str, Enum):
    activo = "activo"
    vencido = "vencido"
    devuelto = "devuelto"


class PrestamoCrear(BaseModel):
    libro_id: int = Field(..., gt=0, description="ID del libro a prestar")
    socio_id: int = Field(..., gt=0, description="ID del socio solicitante")
    fecha_prestamo: date = Field(
        default_factory=date.today,
        description="Fecha de inicio del préstamo (no puede ser futura)"
    )
    dias: int = Field(
        default=14,
        ge=1,
        le=30,
        description="Días de duración del préstamo (entre 1 y 30)"
    )

    @field_validator("fecha_prestamo")
    @classmethod
    def validar_fecha_no_futura(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("La fecha de préstamo no puede ser futura")
        return v


class DevolucionCrear(BaseModel):
    fecha_devolucion: date = Field(
        default_factory=date.today,
        description="Fecha en que se realiza la devolución"
    )


class PrestamoRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    libro_id: int
    socio_id: int
    fecha_prestamo: date
    fecha_limite: date
    fecha_devolucion: date | None = None
    multa: Decimal
    estado: str
    libro: LibroRespuestaSimple | None = None
    socio: SocioRespuestaSimple | None = None
