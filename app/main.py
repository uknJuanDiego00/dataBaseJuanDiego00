from contextlib import asynccontextmanager
# pyrefly: ignore[missing-import]
from fastapi import FastAPI, Request
# pyrefly: ignore[missing-import]
from fastapi.responses import JSONResponse
from .core.database import Base, engine
from .core.exceptions import ErrorAplicacion
from .routes.autor_router import router as autor_router
from .routes.categoria_router import router as categoria_router
from .routes.libro_router import router as libro_router
from .routes.socio_router import router as socio_router
from .routes.prestamo_router import router as prestamo_router
from .routes.reporte_router import router as reporte_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Asegurar que todas las tablas existan en PostgreSQL al iniciar
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="API Biblioteca SENA",
    description="Backend completo para gestión de biblioteca con FastAPI, SQLAlchemy y PostgreSQL",
    version="1.0.0",
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
        "docs": "/docs"
    }
