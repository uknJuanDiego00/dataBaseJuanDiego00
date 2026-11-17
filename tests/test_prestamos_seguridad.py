from datetime import date, timedelta
import pytest
from fastapi.testclient import TestClient


def test_caso_15_prestamo_con_bibliotecario_responsable(client: TestClient, tokens_iniciales: dict):
    """Caso 15: Registro de préstamo asignando registrado_por_id del bibliotecario responsable (Regla Z7)."""
    biblio_token = tokens_iniciales["biblio"]
    socio1_id = tokens_iniciales["socio1_id"]

    res = client.post(
        "/api/v1/prestamos",
        headers={"Authorization": f"Bearer {biblio_token}"},
        json={
            "libro_id": 1,
            "socio_id": socio1_id,
            "dias": 14
        }
    )
    assert res.status_code == 201
    data = res.json()
    assert data["registrado_por_id"] is not None
    assert data["socio_id"] == socio1_id


def test_caso_16_prestamo_a_otro_socio(client: TestClient, tokens_iniciales: dict):
    """Caso 16: El bibliotecario puede registrar préstamos para cualquier socio."""
    biblio_token = tokens_iniciales["biblio"]
    socio2_id = tokens_iniciales["socio2_id"]

    res = client.post(
        "/api/v1/prestamos",
        headers={"Authorization": f"Bearer {biblio_token}"},
        json={
            "libro_id": 1,
            "socio_id": socio2_id,
            "dias": 14
        }
    )
    assert res.status_code == 201
    assert res.json()["socio_id"] == socio2_id


def test_caso_17_filtrado_prestamos_propios_socio(client: TestClient, tokens_iniciales: dict):
    """Caso 17: Un socio solo recibe sus propios préstamos, incluso enviando otro socio_id (Regla Z3)."""
    socio1_token = tokens_iniciales["socio1"]
    socio1_id = tokens_iniciales["socio1_id"]
    socio2_id = tokens_iniciales["socio2_id"]

    # Socio 1 consulta pasando socio_id=socio2_id en query param
    res = client.get(
        f"/api/v1/prestamos?socio_id={socio2_id}",
        headers={"Authorization": f"Bearer {socio1_token}"}
    )
    assert res.status_code == 200
    items = res.json()["items"]
    # Todos los préstamos deben pertenecer a socio 1
    for p in items:
        assert p["socio_id"] == socio1_id


def test_caso_18_socio_consulta_prestamo_ajeno_recibe_404(client: TestClient, tokens_iniciales: dict):
    """Caso 18: Un socio que intente consultar un préstamo ajeno recibe 404 NoEncontrado (Regla Z2)."""
    biblio_token = tokens_iniciales["biblio"]
    socio1_token = tokens_iniciales["socio1"]
    socio2_id = tokens_iniciales["socio2_id"]

    # Crear préstamo perteneciente a socio 2
    res_p2 = client.post(
        "/api/v1/prestamos",
        headers={"Authorization": f"Bearer {biblio_token}"},
        json={"libro_id": 1, "socio_id": socio2_id, "dias": 7}
    )
    p2_id = res_p2.json()["id"]

    # Socio 1 intenta consultar el préstamo de Socio 2 por ID
    res_ajeno = client.get(
        f"/api/v1/prestamos/{p2_id}",
        headers={"Authorization": f"Bearer {socio1_token}"}
    )
    assert res_ajeno.status_code == 404
    assert "no encontrado" in res_ajeno.json()["detail"].lower()


def test_caso_28_devolucion_retraso_calculo_multa(client: TestClient, tokens_iniciales: dict):
    """Caso 28: Préstamo devuelto con retraso genera multa ($0.50/día) con multa_pagada = False."""
    biblio_token = tokens_iniciales["biblio"]
    socio2_id = tokens_iniciales["socio2_id"]

    # Crear préstamo con fecha pasada
    fecha_hace_10 = date.today() - timedelta(days=10)
    res_p = client.post(
        "/api/v1/prestamos",
        headers={"Authorization": f"Bearer {biblio_token}"},
        json={"libro_id": 1, "socio_id": socio2_id, "fecha_prestamo": str(fecha_hace_10), "dias": 5}
    )
    pid = res_p.json()["id"]

    # Devolver hoy (5 días de retraso -> multa $2.50)
    dev_res = client.post(
        f"/api/v1/prestamos/{pid}/devolucion",
        headers={"Authorization": f"Bearer {biblio_token}"},
        json={"fecha_devolucion": str(date.today())}
    )
    assert dev_res.status_code == 200
    data = dev_res.json()
    assert float(data["multa"]) == 2.50
    assert data["multa_pagada"] is False


def test_caso_29_bloqueo_prestamo_por_multa_pendiente(client: TestClient, tokens_iniciales: dict):
    """Caso 29: Un socio con multas pendientes no puede solicitar otro préstamo (Regla R11 -> 422)."""
    biblio_token = tokens_iniciales["biblio"]
    socio2_id = tokens_iniciales["socio2_id"]

    # Socio 2 tiene la multa del Caso 28 pendiente
    res = client.post(
        "/api/v1/prestamos",
        headers={"Authorization": f"Bearer {biblio_token}"},
        json={"libro_id": 1, "socio_id": socio2_id, "dias": 7}
    )
    assert res.status_code == 422
    assert "multas pendientes" in res.json()["detail"].lower()


def test_caso_30_pago_de_multa(client: TestClient, tokens_iniciales: dict):
    """Caso 30: Pago exitoso de multa pendiente -> 200 y multa_pagada = True."""
    biblio_token = tokens_iniciales["biblio"]
    socio2_token = tokens_iniciales["socio2"]
    socio2_id = tokens_iniciales["socio2_id"]

    # Buscar préstamo con multa de socio 2
    prestamos_res = client.get(
        "/api/v1/socios/me/multas",
        headers={"Authorization": f"Bearer {socio2_token}"}
    )
    multas = prestamos_res.json()["items"]
    assert len(multas) > 0
    p_con_multa = multas[0]
    pid = p_con_multa["id"]

    # Socio 2 paga su multa
    pago_res = client.post(
        f"/api/v1/prestamos/{pid}/pago-multa",
        headers={"Authorization": f"Bearer {socio2_token}"}
    )
    assert pago_res.status_code == 200
    assert pago_res.json()["multa_pagada"] is True

    # Intentar pagar nuevamente -> 409 Conflicto
    pago_dupl = client.post(
        f"/api/v1/prestamos/{pid}/pago-multa",
        headers={"Authorization": f"Bearer {socio2_token}"}
    )
    assert pago_dupl.status_code == 409

