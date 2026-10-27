
from datetime import date, timedelta
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base, engine


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Limpia y recrea las tablas antes de ejecutar la suite de pruebas."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture(scope="session")
def client():
    return TestClient(app)


def test_taller_completo(client: TestClient):
    # -------------------------------------------------------------
    # CARGA INICIAL DE DATOS
    # -------------------------------------------------------------

    # 1. Autores
    res_a1 = client.post("/autores", json={
        "nombre": "Mario Vargas Llosa",
        "nacionalidad": "Peruana",
        "anio_nacimiento": 1936
    })
    assert res_a1.status_code == 201
    a1_id = res_a1.json()["id"]

    res_a2 = client.post("/autores", json={
        "nombre": "Laura Restrepo",
        "nacionalidad": "Colombiana",
        "anio_nacimiento": 1950
    })
    assert res_a2.status_code == 201
    a2_id = res_a2.json()["id"]

    res_a3 = client.post("/autores", json={
        "nombre": "Aldous Huxley",
        "nacionalidad": "Británica",
        "anio_nacimiento": 1894
    })
    assert res_a3.status_code == 201
    a3_id = res_a3.json()["id"]

    # 2. Categorías
    res_c1 = client.post("/categorias", json={
        "nombre": "Ficción",
        "descripcion": "Narraciones de hechos imaginarios"
    })
    assert res_c1.status_code == 201
    c1_id = res_c1.json()["id"]

    res_c2 = client.post("/categorias", json={
        "nombre": "Novela histórica",
        "descripcion": "Narraciones ambientadas en épocas pasadas"
    })
    assert res_c2.status_code == 201
    c2_id = res_c2.json()["id"]

    res_c3 = client.post("/categorias", json={
        "nombre": "Ciencia ficción",
        "descripcion": "Relatos sobre ciencia y futuros imaginarios"
    })
    assert res_c3.status_code == 201
    c3_id = res_c3.json()["id"]

    res_c4 = client.post("/categorias", json={
        "nombre": "Ensayo",
        "descripcion": "Textos de análisis y reflexión"
    })
    assert res_c4.status_code == 201
    c4_id = res_c4.json()["id"]

    # 3. Libros
    # Libro 1: La ciudad y los perros
    res_l1 = client.post("/libros", json={
        "titulo": "La ciudad y los perros",
        "isbn": "9788420471839",
        "anio_publicacion": 1963,
        "ejemplares": 2,
        "autor_id": a1_id,
        "categoria_ids": [c1_id, c2_id]
    })
    assert res_l1.status_code == 201
    l1_id = res_l1.json()["id"]

    # Libro 2: La fiesta del Chivo
    res_l2 = client.post("/libros", json={
        "titulo": "La fiesta del Chivo",
        "isbn": "9788420467245",
        "anio_publicacion": 2000,
        "ejemplares": 1,
        "autor_id": a1_id,
        "categoria_ids": [c1_id]
    })
    assert res_l2.status_code == 201
    l2_id = res_l2.json()["id"]

    # Libro 3: Delirio
    res_l3 = client.post("/libros", json={
        "titulo": "Delirio",
        "isbn": "9789587043279",
        "anio_publicacion": 2004,
        "ejemplares": 2,
        "autor_id": a2_id,
        "categoria_ids": [c1_id, c2_id]
    })
    assert res_l3.status_code == 201
    l3_id = res_l3.json()["id"]

    # Libro 4: Un mundo feliz
    res_l4 = client.post("/libros", json={
        "titulo": "Un mundo feliz",
        "isbn": "9780060850524",
        "anio_publicacion": 1932,
        "ejemplares": 3,
        "autor_id": a3_id,
        "categoria_ids": [c1_id, c3_id]
    })
    assert res_l4.status_code == 201
    l4_id = res_l4.json()["id"]

    # 4. Socios
    res_s1 = client.post("/socios", json={
        "nombre": "Carolina Méndez",
        "email": "carolina@example.com",
        "telefono": "+57 3014567890"
    })
    assert res_s1.status_code == 201
    s1_id = res_s1.json()["id"]

    res_s2 = client.post("/socios", json={
        "nombre": "Andrés Ramírez",
        "email": "andres@example.com",
        "telefono": "3117654321"
    })
    assert res_s2.status_code == 201
    s2_id = res_s2.json()["id"]

    res_s3 = client.post("/socios", json={
        "nombre": "Valentina Castro",
        "email": "valentina@example.com",
        "telefono": "3152233445"
    })
    assert res_s3.status_code == 201
    s3_id = res_s3.json()["id"]

    # -------------------------------------------------------------
    # EJECUCIÓN DE LOS 24 CASOS DE PRUEBA
    # -------------------------------------------------------------

    # Caso 1: Crear un autor duplicado -> 409
    c1 = client.post("/autores", json={
        "nombre": "Mario Vargas Llosa",
        "nacionalidad": "Peruana"
    })
    assert c1.status_code == 409, (
        f"Caso 1 falló: esperado 409, obtenido {c1.status_code}"
    )

    # Caso 2: ISBN inválido -> 422
    c2 = client.post("/libros", json={
        "titulo": "Libro Inválido",
        "isbn": "123",
        "anio_publicacion": 2000,
        "ejemplares": 1,
        "autor_id": a1_id,
        "categoria_ids": [c1_id]
    })
    assert c2.status_code == 422, (
        f"Caso 2 falló: esperado 422, obtenido {c2.status_code}"
    )

    # Caso 3: Categorías duplicadas -> 422
    c3 = client.post("/libros", json={
        "titulo": "Libro con Categorías Duplicadas",
        "isbn": "9781234567890",
        "anio_publicacion": 2000,
        "ejemplares": 1,
        "autor_id": a1_id,
        "categoria_ids": [c1_id, c1_id]
    })
    assert c3.status_code == 422, (
        f"Caso 3 falló: esperado 422, obtenido {c3.status_code}"
    )

    # Caso 4: Autor inexistente -> 404
    c4 = client.post("/libros", json={
        "titulo": "Libro sin Autor",
        "isbn": "9781234567890",
        "anio_publicacion": 2000,
        "ejemplares": 1,
        "autor_id": 99,
        "categoria_ids": [c1_id]
    })
    assert c4.status_code == 404, (
        f"Caso 4 falló: esperado 404, obtenido {c4.status_code}"
    )

    # Caso 5: Filtrar por novela histórica y ordenar por año descendente
    c5 = client.get(f"/libros?categoria_id={c2_id}&orden=-anio")
    assert c5.status_code == 200
    libros_historicos = c5.json()
    assert len(libros_historicos) == 2
    assert (
        libros_historicos[0]["anio_publicacion"]
        >= libros_historicos[1]["anio_publicacion"]
    )
    assert libros_historicos[0]["id"] == l3_id
    assert libros_historicos[1]["id"] == l1_id

    # Caso 6: Buscar los libros de Mario Vargas Llosa
    c6 = client.get("/libros?autor=mario")
    assert c6.status_code == 200
    libros_mario = c6.json()
    assert len(libros_mario) == 2
    ids_mario = {libro["id"] for libro in libros_mario}
    assert ids_mario == {l1_id, l2_id}

    # Caso 7: Préstamo del libro 2 al socio 1 -> 201, activo
    c7 = client.post("/prestamos", json={
        "libro_id": l2_id,
        "socio_id": s1_id,
        "dias": 14
    })
    assert c7.status_code == 201
    assert c7.json()["estado"] == "activo"

    # Caso 8: Prestar nuevamente el libro 2 -> 422, sin ejemplares
    c8 = client.post("/prestamos", json={
        "libro_id": l2_id,
        "socio_id": s2_id
    })
    assert c8.status_code == 422
    assert "no hay ejemplares" in c8.json()["detail"].lower()

    # Caso 9: Consultar disponibilidad del libro 2 -> 0
    c9 = client.get(f"/libros/{l2_id}")
    assert c9.status_code == 200
    assert c9.json()["disponibles"] == 0

    # Caso 10: Préstamo vencido del libro 1
    fecha_hace_20 = date.today() - timedelta(days=20)
    c10 = client.post("/prestamos", json={
        "libro_id": l1_id,
        "socio_id": s2_id,
        "fecha_prestamo": str(fecha_hace_20),
        "dias": 7
    })
    assert c10.status_code == 201
    assert c10.json()["estado"] == "vencido"
    prestamo_10_id = c10.json()["id"]

    # Caso 11: Socio con préstamo vencido no puede pedir otro libro
    c11 = client.post("/prestamos", json={
        "libro_id": l4_id,
        "socio_id": s2_id
    })
    assert c11.status_code == 422
    assert "vencidos" in c11.json()["detail"].lower()

    # Caso 12: Reporte de préstamos vencidos
    c12 = client.get("/reportes/prestamos-vencidos")
    assert c12.status_code == 200
    vencidos = c12.json()
    p_vencido = next(
        (
            prestamo for prestamo in vencidos
            if prestamo["prestamo_id"] == prestamo_10_id
        ),
        None
    )
    assert p_vencido is not None
    assert p_vencido["dias_retraso"] == 13

    # Caso 13: Devolver el préstamo vencido -> multa de 6.5
    c13 = client.post(
        f"/prestamos/{prestamo_10_id}/devolucion",
        json={"fecha_devolucion": str(date.today())}
    )
    assert c13.status_code == 200
    assert float(c13.json()["multa"]) == 6.5

    # Caso 14: Devolver nuevamente el préstamo -> 409
    c14 = client.post(
        f"/prestamos/{prestamo_10_id}/devolucion"
    )
    assert c14.status_code == 409

    # Caso 15: Máximo de tres préstamos por socio
    p_s3_1 = client.post("/prestamos", json={
        "libro_id": l1_id,
        "socio_id": s3_id
    })
    assert p_s3_1.status_code == 201

    p_s3_2 = client.post("/prestamos", json={
        "libro_id": l3_id,
        "socio_id": s3_id
    })
    assert p_s3_2.status_code == 201

    p_s3_3 = client.post("/prestamos", json={
        "libro_id": l4_id,
        "socio_id": s3_id
    })
    assert p_s3_3.status_code == 201

    p_s3_4 = client.post("/prestamos", json={
        "libro_id": l3_id,
        "socio_id": s3_id
    })
    assert p_s3_4.status_code == 422
    assert "máximo de 3" in p_s3_4.json()["detail"].lower()

    # Caso 16: No permitir cero ejemplares -> 422
    c16 = client.patch(f"/libros/{l4_id}", json={
        "ejemplares": 0
    })
    assert c16.status_code == 422

    # Caso 17: No eliminar un autor que tiene libros -> 409
    c17 = client.delete(f"/autores/{a1_id}")
    assert c17.status_code == 409

    # Caso 18: No eliminar un libro con préstamo sin devolver -> 409
    c18 = client.delete(f"/libros/{l2_id}")
    assert c18.status_code == 409

    # Caso 19: Desactivar socio 2
    c19 = client.delete(f"/socios/{s2_id}")
    assert c19.status_code == 204
    socio_2 = client.get(f"/socios/{s2_id}").json()
    assert socio_2["activo"] is False

    # Caso 20: Un socio inactivo no puede realizar préstamos
    c20 = client.post("/prestamos", json={
        "libro_id": l4_id,
        "socio_id": s2_id
    })
    assert c20.status_code == 422
    assert "no está activo" in c20.json()["detail"].lower()

    # Caso 21: La categoría Ensayo debe aparecer con cero libros
    c21 = client.get("/reportes/categorias")
    assert c21.status_code == 200
    cats_rep = c21.json()
    cat_ensayo = next(
        (
            categoria for categoria in cats_rep
            if categoria["categoria"].lower() == "ensayo"
        ),
        None
    )
    assert cat_ensayo is not None
    assert cat_ensayo["total_libros"] == 0

    # Caso 22: Reporte de socios con multas
    c22 = client.get("/reportes/socios-con-multas")
    assert c22.status_code == 200
    multas_rep = c22.json()
    assert len(multas_rep) == 1
    assert multas_rep[0]["socio"] == "Andrés Ramírez"
    assert float(multas_rep[0]["total_multas"]) == 6.5

    # Caso 23: Reporte de los tres libros más prestados
    c23 = client.get("/reportes/libros-mas-prestados?limite=3")
    assert c23.status_code == 200
    mas_prestados = c23.json()
    assert len(mas_prestados) == 3

    for i in range(len(mas_prestados) - 1):
        assert (
            mas_prestados[i]["total_prestamos"]
            >= mas_prestados[i + 1]["total_prestamos"]
        )

    # Caso 24: Paginación sin repetir libros
    c24_pag1 = client.get("/libros?skip=0&limit=2")
    assert c24_pag1.status_code == 200
    pag1 = c24_pag1.json()
    assert len(pag1) == 2

    c24_pag2 = client.get("/libros?skip=2&limit=2")
    assert c24_pag2.status_code == 200
    pag2 = c24_pag2.json()
    assert len(pag2) == 2

    ids_pag1 = {libro["id"] for libro in pag1}
    ids_pag2 = {libro["id"] for libro in pag2}

    assert ids_pag1.isdisjoint(ids_pag2), (
        "Las páginas de libros no deben contener elementos repetidos"
    )
