
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.responses import Response

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from .core.config import settings
from .core.exceptions import ErrorAplicacion

# ------------------------------------------------------------------
# IMPORTAR ROUTERS
# ------------------------------------------------------------------
from .routes.health_router import router as health_router
from .routes.autor_router import router as autor_router
from .routes.categoria_router import router as categoria_router
from .routes.libro_router import router as libro_router
from .routes.socio_router import router as socio_router
from .routes.prestamo_router import router as prestamo_router
from .routes.reporte_router import router as reporte_router
from .routes.auth_router import router as auth_router
from .routes.usuario_router import router as usuario_router


# ------------------------------------------------------------------
# CONFIGURACIÓN DE LOGGING
# ------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------
# CONFIGURACIÓN RATE LIMITING
# ------------------------------------------------------------------
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[]
)


# ------------------------------------------------------------------
# LIFESPAN
# ------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando API de Biblioteca...")
    yield
    logger.info("Cerrando API de Biblioteca...")


# ------------------------------------------------------------------
# CREACIÓN DE FASTAPI
# ------------------------------------------------------------------
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Backend para gestión de biblioteca con FastAPI, "
        "PostgreSQL, autenticación JWT y migraciones"
    ),
    version=settings.VERSION,
    lifespan=lifespan
)


# ------------------------------------------------------------------
# MANEJADOR PERSONALIZADO DE RATE LIMITING
# ------------------------------------------------------------------
async def rate_limit_handler(
    request: Request,
    exc: Exception
) -> Response:

    if isinstance(exc, RateLimitExceeded):
        return _rate_limit_exceeded_handler(request, exc)

    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor"}
    )


# ------------------------------------------------------------------
# REGISTRO DE RATE LIMITING
# ------------------------------------------------------------------
app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    rate_limit_handler
)


# ------------------------------------------------------------------
# CONFIGURACIÓN CORS
# ------------------------------------------------------------------
cors_origins = (
    settings.CORS_ORIGINS
    if isinstance(settings.CORS_ORIGINS, list)
    else ["*"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins if cors_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ------------------------------------------------------------------
# MANEJADOR DE EXCEPCIONES PERSONALIZADAS
# ------------------------------------------------------------------
@app.exception_handler(ErrorAplicacion)
async def error_aplicacion_handler(
    request: Request,
    exc: ErrorAplicacion
):
    headers = {}

    if exc.status_code == 401:
        headers["WWW-Authenticate"] = "Bearer"

    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.mensaje},
        headers=headers or None
    )


# ------------------------------------------------------------------
# REGISTRO DE ROUTERS
# ------------------------------------------------------------------
PREFIX = settings.API_V1_STR

# Routers que ya tienen su propio prefijo
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(usuario_router)

# Routers versionados
app.include_router(autor_router, prefix=PREFIX)
app.include_router(categoria_router, prefix=PREFIX)
app.include_router(libro_router, prefix=PREFIX)
app.include_router(socio_router, prefix=PREFIX)
app.include_router(prestamo_router, prefix=PREFIX)
app.include_router(reporte_router, prefix=PREFIX)


# ------------------------------------------------------------------
# RUTA PRINCIPAL
# ------------------------------------------------------------------
@app.get("/", tags=["Salud"])
async def root():
    return {
        "mensaje": "API de Biblioteca en ejecución",
        "health": f"{PREFIX}/health",
        "docs": "/docs",
        "version": settings.VERSION
    }


# ------------------------------------------------------------------
# ESTADO DE LA API
# ------------------------------------------------------------------
@app.get("/api/status", tags=["Salud"])
async def api_status():
    return {
        "status": "online",
        "mensaje": "El servidor está funcionando correctamente"
    }
