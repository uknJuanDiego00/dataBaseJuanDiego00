from collections.abc import Generator
from typing import Annotated
from fastapi import Depends, Query
from sqlalchemy.orm import Session
from .database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Generador que provee una sesión de base de datos por petición."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


SessionDep = Annotated[Session, Depends(get_db)]


class Paginacion:
    """Parámetros reutilizables de paginación."""
    def __init__(
        self,
        skip: int = Query(default=0, ge=0, description="Registros a omitir"),
        limit: int = Query(default=10, ge=1, le=100, description="Límite de registros por página (máx. 100)")
    ):
        self.skip = skip
        self.limit = limit


PaginacionDep = Annotated[Paginacion, Depends(Paginacion)]
