from fastapi import APIRouter, Query, status
from ..controllers import autor_controller, libro_controller
from ..core.dependencies import PaginacionDep, SessionDep
from ..schemas.autor import AutorActualizar, AutorCrear, AutorRespuesta
from ..schemas.libro import LibroRespuesta

router = APIRouter(
    prefix="/autores",
    tags=["Autores"]
)


@router.get("", response_model=list[AutorRespuesta], status_code=status.HTTP_200_OK)
def listar_autores(
    db: SessionDep,
    paginacion: PaginacionDep,
    nacionalidad: str | None = Query(default=None, description="Filtrar por nacionalidad")
):
    """Lista paginada de autores con filtro opcional por nacionalidad."""
    return autor_controller.listar_autores(
        db=db,
        skip=paginacion.skip,
        limit=paginacion.limit,
        nacionalidad=nacionalidad
    )


@router.get("/{id}", response_model=AutorRespuesta, status_code=status.HTTP_200_OK)
def obtener_autor(id: int, db: SessionDep):
    """Consulta un autor por su ID."""
    return autor_controller.obtener_autor(db=db, autor_id=id)


@router.post("", response_model=AutorRespuesta, status_code=status.HTTP_201_CREATED)
def crear_autor(datos: AutorCrear, db: SessionDep):
    """Crea un nuevo autor en el sistema."""
    return autor_controller.crear_autor(db=db, datos=datos)


@router.patch("/{id}", response_model=AutorRespuesta, status_code=status.HTTP_200_OK)
def actualizar_autor(id: int, datos: AutorActualizar, db: SessionDep):
    """Actualiza solo los campos enviados de un autor."""
    return autor_controller.actualizar_autor(db=db, autor_id=id, datos=datos)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_autor(id: int, db: SessionDep):
    """Elimina un autor por su ID si no tiene libros dependientes."""
    autor_controller.eliminar_autor(db=db, autor_id=id)
    return None


@router.get("/{id}/libros", response_model=list[LibroRespuesta], status_code=status.HTTP_200_OK)
def listar_libros_de_autor(id: int, db: SessionDep, paginacion: PaginacionDep):
    """Lista los libros de un autor específico."""
    return libro_controller.listar_libros_por_autor(
        db=db,
        autor_id=id,
        skip=paginacion.skip,
        limit=paginacion.limit
    )

