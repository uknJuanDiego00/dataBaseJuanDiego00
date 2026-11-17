from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from .core.config import settings
from .core.exceptions import ErrorAplicacion
from .routes.autor_router import router as autor_router
from .routes.categoria_router import router as categoria_router
from .routes.libro_router import router as libro_router
from .routes.socio_router import router as socio_router
from .routes.prestamo_router import router as prestamo_router
from .routes.reporte_router import router as reporte_router
from .routes.health_router import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend para gestión de biblioteca con FastAPI, PostgreSQL, autenticación JWT y migraciones",
    version=settings.VERSION,
    lifespan=lifespan
)


# Manejador centralizado para todas las excepciones propias de la aplicación
@app.exception_handler(ErrorAplicacion)
async def error_aplicacion_handler(request: Request, exc: ErrorAplicacion):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.mensaje}
    )


# Registro de routers
app.include_router(health_router)
app.include_router(autor_router)
app.include_router(categoria_router)
app.include_router(libro_router)
app.include_router(socio_router)
app.include_router(prestamo_router)
app.include_router(reporte_router)


@app.get("/", tags=["Salud"])
def root():
    return {
        "mensaje": "API de Biblioteca en ejecución",
        "health": "/api/v1/health",
        "docs": "/docs"
    }
