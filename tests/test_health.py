from fastapi.testclient import TestClient


def test_caso_31_endpoint_health(client: TestClient):
    """Caso 31: Endpoint GET /api/v1/health verifica estado de la API y de PostgreSQL."""
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["database"] == "conectada"
    assert "environment" in data
    assert "version" in data

