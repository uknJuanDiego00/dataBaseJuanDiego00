import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from .core.config import settings
from .core.exceptions import ErrorAplicacion

# ------------------------------------------------------------------
# Importar todos los routers
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
# Logging
# ------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# Rate limiting
# ------------------------------------------------------------------
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando API Biblioteca v%s [%s]", settings.VERSION, settings.ENVIRONMENT)
    yield
    logger.info("Cerrando API Biblioteca")


# ------------------------------------------------------------------
# Configuración de FastAPI según entorno
# ------------------------------------------------------------------
_docs_url = None if settings.ENVIRONMENT == "production" else "/docs"
_redoc_url = None if settings.ENVIRONMENT == "production" else "/redoc"

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Backend para gestión de biblioteca con FastAPI, PostgreSQL, "
        "autenticación JWT, autorización por roles y migraciones Alembic."
    ),
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url=_docs_url,
    redoc_url=_redoc_url,
)

# ------------------------------------------------------------------
# Rate limiting state
# ------------------------------------------------------------------
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ------------------------------------------------------------------
# CORS
# ------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if settings.ENVIRONMENT != "production" else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------
# Middleware: Request-ID y logging estructurado
# ------------------------------------------------------------------
@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    start_time = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
    response.headers["X-Request-ID"] = request_id

    # No registrar contraseñas ni tokens
    path = request.url.path
    method = request.method
    logger.info(
        "method=%s path=%s status=%d duration_ms=%.2f request_id=%s",
        method, path, response.status_code, duration_ms, request_id
    )
    return response


# ------------------------------------------------------------------
# Manejadores de excepciones
# ------------------------------------------------------------------
@app.exception_handler(ErrorAplicacion)
async def error_aplicacion_handler(request: Request, exc: ErrorAplicacion):
    headers = {}
    if exc.status_code == 401:
        headers["WWW-Authenticate"] = "Bearer"
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.mensaje},
        headers=headers or None
    )


@app.exception_handler(Exception)
async def error_generico_handler(request: Request, exc: Exception):
    logger.exception("Error inesperado en %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Error interno del servidor"}
    )


# ------------------------------------------------------------------
# Registro de routers
# ------------------------------------------------------------------
PREFIX = settings.API_V1_STR  # "/api/v1"

# Rutas estándar versionadas bajo /api/v1 (Taller 2)
app.include_router(health_router)       # ya tiene prefix /api/v1/health
app.include_router(auth_router)         # prefix /api/v1/auth
app.include_router(usuario_router)      # prefix /api/v1/usuarios
app.include_router(autor_router, prefix=PREFIX)
app.include_router(categoria_router, prefix=PREFIX)
app.include_router(libro_router, prefix=PREFIX)
app.include_router(socio_router, prefix=PREFIX)
app.include_router(prestamo_router, prefix=PREFIX)
app.include_router(reporte_router, prefix=PREFIX)

# Compatibilidad con rutas sin prefijo del Taller 1
app.include_router(autor_router)
app.include_router(categoria_router)
app.include_router(libro_router)
app.include_router(socio_router)
app.include_router(prestamo_router)
app.include_router(reporte_router)



@app.get("/", tags=["Salud"], summary="Raíz de la API")
def root():
    return {
        "mensaje": "API de Biblioteca en ejecución",
        "health": f"{PREFIX}/health",
        "docs": "/docs" if _docs_url else "No disponible en producción"
    }
