from datetime import date, timedelta
from decimal import Decimal
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
    res_a1 = client.post("/autores", json={"nombre": "Gabriel García Márquez", "nacionalidad": "Colombiana", "anio_nacimiento": 1927})
    assert res_a1.status_code == 201
    a1_id = res_a1.json()["id"]

    res_a2 = client.post("/autores", json={"nombre": "Isabel Allende", "nacionalidad": "Chilena", "anio_nacimiento": 1942})
    assert res_a2.status_code == 201
    a2_id = res_a2.json()["id"]

    res_a3 = client.post("/autores", json={"nombre": "George Orwell", "nacionalidad": "Británica", "anio_nacimiento": 1903})
    assert res_a3.status_code == 201
    a3_id = res_a3.json()["id"]

    # 2. Categorías
    res_c1 = client.post("/categorias", json={"nombre": "Novela", "descripcion": "Obras narrativas de ficción"})
    assert res_c1.status_code == 201
    c1_id = res_c1.json()["id"]

    res_c2 = client.post("/categorias", json={"nombre": "Realismo Mágico", "descripcion": "Elementos mágicos en contextos reales"})
    assert res_c2.status_code == 201
    c2_id = res_c2.json()["id"]

    res_c3 = client.post("/categorias", json={"nombre": "Distopía", "descripcion": "Sociedades ficticias indeseables"})
    assert res_c3.status_code == 201
    c3_id = res_c3.json()["id"]

    res_c4 = client.post("/categorias", json={"nombre": "Poesía", "descripcion": "Composiciones líricas"})
    assert res_c4.status_code == 201
    c4_id = res_c4.json()["id"]

    # 3. Libros
    # Libro 1: Cien años de soledad (1967, 2 ejemplares, autor 1, categorías 1 y 2)
    res_l1 = client.post("/libros", json={
        "titulo": "Cien años de soledad",
        "isbn": "9780307474728",
        "anio_publicacion": 1967,
        "ejemplares": 2,
        "autor_id": a1_id,
        "categoria_ids": [c1_id, c2_id]
    })
    assert res_l1.status_code == 201
    l1_id = res_l1.json()["id"]

    # Libro 2: El amor en los tiempos del cólera (1985, 1 ejemplar, autor 1, categoría 1)
    res_l2 = client.post("/libros", json={
        "titulo": "El amor en los tiempos del cólera",
        "isbn": "9780307389732",
        "anio_publicacion": 1985,
        "ejemplares": 1,
        "autor_id": a1_id,
        "categoria_ids": [c1_id]
    })
    assert res_l2.status_code == 201
    l2_id = res_l2.json()["id"]

    # Libro 3: La casa de los espíritus (1982, 2 ejemplares, autor 2, categorías 1 y 2)
    res_l3 = client.post("/libros", json={
        "titulo": "La casa de los espíritus",
        "isbn": "9780525433446",
        "anio_publicacion": 1982,
        "ejemplares": 2,
        "autor_id": a2_id,
        "categoria_ids": [c1_id, c2_id]
    })
    assert res_l3.status_code == 201
    l3_id = res_l3.json()["id"]

    # Libro 4: 1984 (1949, 3 ejemplares, autor 3, categorías 1 y 3)
    res_l4 = client.post("/libros", json={
        "titulo": "1984",
        "isbn": "9780451524935",
        "anio_publicacion": 1949,
        "ejemplares": 3,
        "autor_id": a3_id,
        "categoria_ids": [c1_id, c3_id]
    })
    assert res_l4.status_code == 201
    l4_id = res_l4.json()["id"]

    # 4. Socios
    res_s1 = client.post("/socios", json={"nombre": "Ana Torres", "email": "ANA@example.com", "telefono": "+57 3001234567"})
    assert res_s1.status_code == 201
    s1_id = res_s1.json()["id"]

    res_s2 = client.post("/socios", json={"nombre": "Luis Pérez", "email": "luis@example.com", "telefono": "3109876543"})
    assert res_s2.status_code == 201
    s2_id = res_s2.json()["id"]

    res_s3 = client.post("/socios", json={"nombre": "Marta Ruiz", "email": "marta@example.com", "telefono": "3201122334"})
    assert res_s3.status_code == 201
    s3_id = res_s3.json()["id"]

    # -------------------------------------------------------------
    # EJECUCIÓN DE LOS 24 CASOS DE PRUEBA
    # -------------------------------------------------------------

    # Caso 1: POST /autores con "Gabriel García Márquez" otra vez -> 409
    c1 = client.post("/autores", json={"nombre": "Gabriel García Márquez", "nacionalidad": "Colombiana"})
    assert c1.status_code == 409, f"Caso 1 fallo: esperado 409, obtenido {c1.status_code}"

    # Caso 2: POST /libros con "isbn": "123" -> 422
    c2 = client.post("/libros", json={
        "titulo": "Libro Inválido",
        "isbn": "123",
        "anio_publicacion": 2000,
        "ejemplares": 1,
        "autor_id": a1_id,
        "categoria_ids": [c1_id]
    })
    assert c2.status_code == 422, f"Caso 2 fallo: esperado 422, obtenido {c2.status_code}"

    # Caso 3: POST /libros con "categoria_ids": [1, 1] -> 422
    c3 = client.post("/libros", json={
        "titulo": "Libro Categorías Duplicadas",
        "isbn": "9781234567890",
        "anio_publicacion": 2000,
        "ejemplares": 1,
        "autor_id": a1_id,
        "categoria_ids": [c1_id, c1_id]
    })
    assert c3.status_code == 422, f"Caso 3 fallo: esperado 422, obtenido {c3.status_code}"

    # Caso 4: POST /libros con "autor_id": 99 -> 404
    c4 = client.post("/libros", json={
        "titulo": "Libro Sin Autor",
        "isbn": "9781234567890",
        "anio_publicacion": 2000,
        "ejemplares": 1,
        "autor_id": 99,
        "categoria_ids": [c1_id]
    })
    assert c4.status_code == 404, f"Caso 4 fallo: esperado 404, obtenido {c4.status_code}"

    # Caso 5: GET /libros?categoria_id=2&orden=-anio -> Los 2 libros de realismo mágico, el más nuevo primero
    c5 = client.get(f"/libros?categoria_id={c2_id}&orden=-anio")
    assert c5.status_code == 200
    libros_rm = c5.json()
    assert len(libros_rm) == 2
    # El más nuevo primero: 1982 (La Casa De Los Espíritus), 1967 (Cien Años De Soledad)
    assert libros_rm[0]["anio_publicacion"] >= libros_rm[1]["anio_publicacion"]
    assert libros_rm[0]["id"] == l3_id
    assert libros_rm[1]["id"] == l1_id

    # Caso 6: GET /libros?autor=gabriel -> Los 2 libros de García Márquez
    c6 = client.get("/libros?autor=gabriel")
    assert c6.status_code == 200
    libros_gabriel = c6.json()
    assert len(libros_gabriel) == 2
    ids_gabriel = {l["id"] for l in libros_gabriel}
    assert ids_gabriel == {l1_id, l2_id}

    # Caso 7: Préstamo del libro 2 al socio 1 -> 201, estado activo
    c7 = client.post("/prestamos", json={"libro_id": l2_id, "socio_id": s1_id, "dias": 14})
    assert c7.status_code == 201
    assert c7.json()["estado"] == "activo"

    # Caso 8: Préstamo del libro 2 al socio 2 -> 422, no hay ejemplares
    c8 = client.post("/prestamos", json={"libro_id": l2_id, "socio_id": s2_id})
    assert c8.status_code == 422
    assert "no hay ejemplares" in c8.json()["detail"].lower()

    # Caso 9: GET /libros/2 -> disponibles: 0
    c9 = client.get(f"/libros/{l2_id}")
    assert c9.status_code == 200
    assert c9.json()["disponibles"] == 0

    # Caso 10: Préstamo del libro 1 al socio 2 con fecha_prestamo de hace 20 días y dias: 7 -> 201, estado vencido
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

    # Caso 11: Préstamo del libro 4 al socio 2 -> 422, tiene préstamos vencidos
    c11 = client.post("/prestamos", json={"libro_id": l4_id, "socio_id": s2_id})
    assert c11.status_code == 422
    assert "vencidos" in c11.json()["detail"].lower()

    # Caso 12: GET /reportes/prestamos-vencidos -> Aparece el préstamo del caso 10 con dias_retraso: 13
    c12 = client.get("/reportes/prestamos-vencidos")
    assert c12.status_code == 200
    vencidos = c12.json()
    p_vencido = next((p for p in vencidos if p["prestamo_id"] == prestamo_10_id), None)
    assert p_vencido is not None
    assert p_vencido["dias_retraso"] == 13

    # Caso 13: Devolver hoy el préstamo del caso 10 -> 200, multa: 6.5
    c13 = client.post(f"/prestamos/{prestamo_10_id}/devolucion", json={"fecha_devolucion": str(date.today())})
    assert c13.status_code == 200
    assert float(c13.json()["multa"]) == 6.5

    # Caso 14: Devolverlo otra vez -> 409
    c14 = client.post(f"/prestamos/{prestamo_10_id}/devolucion")
    assert c14.status_code == 409

    # Caso 15: Socio 3: préstamos de los libros 1, 3 y 4, y luego un cuarto -> El cuarto responde 422 (máximo 3)
    p_s3_1 = client.post("/prestamos", json={"libro_id": l1_id, "socio_id": s3_id})
    assert p_s3_1.status_code == 201

    p_s3_2 = client.post("/prestamos", json={"libro_id": l3_id, "socio_id": s3_id})
    assert p_s3_2.status_code == 201

    p_s3_3 = client.post("/prestamos", json={"libro_id": l4_id, "socio_id": s3_id})
    assert p_s3_3.status_code == 201

    # Cuarto préstamo (intenta pedir libro 3 disponible de nuevo o libro 4):
    p_s3_4 = client.post("/prestamos", json={"libro_id": l3_id, "socio_id": s3_id})
    assert p_s3_4.status_code == 422
    assert "máximo de 3" in p_s3_4.json()["detail"].lower()

    # Caso 16: PATCH /libros/4 con "ejemplares": 0 -> 422
    c16 = client.patch(f"/libros/{l4_id}", json={"ejemplares": 0})
    assert c16.status_code == 422

    # Caso 17: DELETE /autores/1 -> 409, tiene libros
    c17 = client.delete(f"/autores/{a1_id}")
    assert c17.status_code == 409

    # Caso 18: DELETE /libros/2 -> 409, préstamo sin devolver
    c18 = client.delete(f"/libros/{l2_id}")
    assert c18.status_code == 409

    # Caso 19: DELETE /socios/2 -> 204 y queda activo: false
    c19 = client.delete(f"/socios/{s2_id}")
    assert c19.status_code == 204
    socio_2 = client.get(f"/socios/{s2_id}").json()
    assert socio_2["activo"] is False

    # Caso 20: Cualquier préstamo al socio 2 -> 422, el socio no está activo
    c20 = client.post("/prestamos", json={"libro_id": l4_id, "socio_id": s2_id})
    assert c20.status_code == 422
    assert "no está activo" in c20.json()["detail"].lower()

    # Caso 21: GET /reportes/categorias -> poesía aparece con total_libros: 0
    c21 = client.get("/reportes/categorias")
    assert c21.status_code == 200
    cats_rep = c21.json()
    cat_poesia = next((c for c in cats_rep if c["categoria"] == "poesía"), None)
    assert cat_poesia is not None
    assert cat_poesia["total_libros"] == 0

    # Caso 22: GET /reportes/socios-con-multas -> Solo Luis Pérez, total_multas: 6.5
    c22 = client.get("/reportes/socios-con-multas")
    assert c22.status_code == 200
    multas_rep = c22.json()
    assert len(multas_rep) == 1
    assert multas_rep[0]["socio"] == "Luis Pérez"
    assert float(multas_rep[0]["total_multas"]) == 6.5

    # Caso 23: GET /reportes/libros-mas-prestados?limite=3 -> 3 libros ordenados de mayor a menor
    c23 = client.get("/reportes/libros-mas-prestados?limite=3")
    assert c23.status_code == 200
    mas_prestados = c23.json()
    assert len(mas_prestados) == 3
    for i in range(len(mas_prestados) - 1):
        assert mas_prestados[i]["total_prestamos"] >= mas_prestados[i + 1]["total_prestamos"]

    # Caso 24: GET /libros?skip=0&limit=2 y luego ?skip=2&limit=2 -> 2 libros en cada página, sin repetir
    c24_pag1 = client.get("/libros?skip=0&limit=2")
    assert c24_pag1.status_code == 200
    pag1 = c24_pag1.json()
    assert len(pag1) == 2

    c24_pag2 = client.get("/libros?skip=2&limit=2")
    assert c24_pag2.status_code == 200
    pag2 = c24_pag2.json()
    assert len(pag2) == 2

    ids_pag1 = {l["id"] for l in pag1}
    ids_pag2 = {l["id"] for l in pag2}
    assert ids_pag1.isdisjoint(ids_pag2), "Las páginas de libros no deben contener elementos repetidos"
