from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from .core.database import engine, Base
from .core.exceptions import ErrorAplicacion

# Creación de la aplicación FastAPI
app = FastAPI(
    title="API Biblioteca SENA",
    description="Backend completo para gestión de biblioteca con FastAPI, SQLAlchemy y PostgreSQL",
    version="1.0.0"
)


# Manejador centralizado para todas las excepciones propias de la aplicación
@app.exception_handler(ErrorAplicacion)
async def error_aplicacion_handler(request: Request, exc: ErrorAplicacion):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.mensaje}
    )


@app.get("/", tags=["Salud"])
def root():
    return {
        "mensaje": "API de Biblioteca en ejecución",
        "docs": "/docs"
    }
