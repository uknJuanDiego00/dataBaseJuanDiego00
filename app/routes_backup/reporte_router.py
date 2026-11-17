from fastapi import APIRouter, Depends, Query, status
from ..controllers import reporte_controller
from ..core.dependencies import SessionDep, requiere_rol
from ..models.usuario import RolUsuario
from ..schemas.reporte import (
    AutorEstadisticasItem,
    CategoriaLibrosItem,
    LibroMasPrestadoItem,
    PrestamoVencidoItem,
    ResumenBiblioteca,
    SocioMultasItem
)

router = APIRouter(
    prefix="/reportes",
    tags=["Reportes"],
    dependencies=[Depends(requiere_rol(RolUsuario.bibliotecario, RolUsuario.admin))]
)


@router.get(
    "/libros-mas-prestados",
    response_model=list[LibroMasPrestadoItem],
    status_code=status.HTTP_200_OK,
    summary="Reporte: Libros más prestados",
    responses={
        200: {"description": "Lista de libros más prestados"},
        401: {"description": "No autenticado"},
        403: {"description": "Requiere rol bibliotecario o admin"}
    }
)
def reporte_libros_mas_prestados(
    db: SessionDep,
    limite: int = Query(default=5, ge=1, le=50, description="Cantidad máxima de libros a retornar")
):
    """Reporte de los libros con mayor número de préstamos."""
    return reporte_controller.reporte_libros_mas_prestados(db=db, limite=limite)


@router.get(
    "/categorias",
    response_model=list[CategoriaLibrosItem],
    status_code=status.HTTP_200_OK,
    summary="Reporte: Libros por categoría",
    responses={
        200: {"description": "Total de libros por categoría"},
        401: {"description": "No autenticado"},
        403: {"description": "Requiere rol bibliotecario o admin"}
    }
)
def reporte_categorias(db: SessionDep):
    """Reporte del total de libros asociados a cada categoría, incluidas las que tienen 0 libros."""
    return reporte_controller.reporte_categorias(db=db)


@router.get(
    "/prestamos-vencidos",
    response_model=list[PrestamoVencidoItem],
    status_code=status.HTTP_200_OK,
    summary="Reporte: Préstamos vencidos",
    responses={
        200: {"description": "Detalle de préstamos vencidos no devueltos"},
        401: {"description": "No autenticado"},
        403: {"description": "Requiere rol bibliotecario o admin"}
    }
)
def reporte_prestamos_vencidos(db: SessionDep):
    """Reporte de préstamos vencidos no devueltos con cálculo de días de retraso."""
    return reporte_controller.reporte_prestamos_vencidos(db=db)


@router.get(
    "/socios-con-multas",
    response_model=list[SocioMultasItem],
    status_code=status.HTTP_200_OK,
    summary="Reporte: Socios con multas",
    responses={
        200: {"description": "Socios que acumulan multas"},
        401: {"description": "No autenticado"},
        403: {"description": "Requiere rol bibliotecario o admin"}
    }
)
def reporte_socios_con_multas(db: SessionDep):
    """Reporte de socios que han acumulado multas con el conteo de préstamos multados."""
    return reporte_controller.reporte_socios_con_multas(db=db)


@router.get(
    "/autores",
    response_model=list[AutorEstadisticasItem],
    status_code=status.HTTP_200_OK,
    summary="Reporte: Estadísticas de autores",
    responses={
        200: {"description": "Estadísticas por autor"},
        401: {"description": "No autenticado"},
        403: {"description": "Requiere rol bibliotecario o admin"}
    }
)
def reporte_autores(db: SessionDep):
    """Reporte estadístico de autores con total de libros, ejemplares y préstamos."""
    return reporte_controller.reporte_autores(db=db)


@router.get(
    "/resumen",
    response_model=ResumenBiblioteca,
    status_code=status.HTTP_200_OK,
    summary="Reporte: Resumen ejecutivo global",
    responses={
        200: {"description": "Cuadro de mando general de la biblioteca"},
        401: {"description": "No autenticado"},
        403: {"description": "Requiere rol bibliotecario o admin"}
    }
)
def reporte_resumen(db: SessionDep):
    """Resumen cuantitativo global de la biblioteca en una sola consulta SQL."""
    return reporte_controller.reporte_resumen(db=db)
