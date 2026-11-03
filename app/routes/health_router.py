from fastapi import APIRouter, Response, status
from sqlalchemy import text
from ..core.config import settings
from ..core.dependencies import SessionDep

router = APIRouter(
    prefix="/api/v1/health",
    tags=["Salud"]
)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="Verificar estado de la API y base de datos",
    responses={
        200: {"description": "API y base de datos operativas"},
        503: {"description": "Base de datos no disponible"},
    }
)
def verificar_salud(db: SessionDep, response: Response):
    """
    Verifica el estado de la API y la conexión activa con PostgreSQL.
    Devuelve 503 si la base de datos no responde.
    """
    try:
        db.execute(text("SELECT 1"))
        db_status = "conectada"
        http_status = status.HTTP_200_OK
    except Exception as e:
        db_status = f"desconectada ({str(e)})"
        http_status = status.HTTP_503_SERVICE_UNAVAILABLE
        response.status_code = http_status

    return {
        "status": "ok" if db_status == "conectada" else "degradado",
        "database": db_status,
        "environment": settings.ENVIRONMENT,
        "version": settings.VERSION
    }
