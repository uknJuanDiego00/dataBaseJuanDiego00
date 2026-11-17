
from fastapi import APIRouter, status
from sqlalchemy import text
from ..core.config import settings
from ..core.dependencies import SessionDep

router = APIRouter(
    prefix="/api/v1/health",
    tags=["Salud"]
)


@router.get("", status_code=status.HTTP_200_OK)
def verificar_salud(db: SessionDep):
    """
    Verifica el estado de la API y la conexión activa con PostgreSQL.
    """
    try:
        db.execute(text("SELECT 1"))
        db_status = "conectada"
    except Exception as e:
        db_status = f"desconectada ({str(e)})"

    return {
        "status": "ok" if db_status == "conectada" else "degradado",
        "database": db_status,
        "environment": settings.ENVIRONMENT,
        "version": settings.VERSION
    }
