from datetime import date
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class LibroMasPrestadoItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    libro_id: int
    titulo: str
    autor: str
    total_prestamos: int


class CategoriaLibrosItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    categoria_id: int
    categoria: str
    total_libros: int


class PrestamoVencidoItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    prestamo_id: int
    titulo: str
    socio_id: int
    socio: str
    email: str
    fecha_limite: date
    dias_retraso: int


class SocioMultasItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    socio_id: int
    socio: str
    email: str
    total_multas: Decimal
    prestamos_con_multa: int


class AutorEstadisticasItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    autor_id: int
    autor: str
    total_libros: int
    total_ejemplares: int
    total_prestamos: int


class ResumenBiblioteca(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_libros: int
    total_ejemplares: int
    total_prestados: int
    socios_activos: int
    prestamos_vencidos: int
    total_multas: Decimal
