from fastapi.testclient import TestClient


def test_paginacion_generica_libros(client: TestClient):
    """Verifica que la paginación genérica Pagina[T] incluya items, total, skip y limit."""
    res = client.get("/api/v1/libros?skip=0&limit=2")
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert "total" in data
    assert "skip" in data
    assert "limit" in data
    assert data["skip"] == 0
    assert data["limit"] == 2
    assert isinstance(data["items"], list)
    assert data["total"] >= len(data["items"])


def test_paginacion_generica_autores(client: TestClient):
    """Verifica la estructura Pagina[T] en el endpoint de autores."""
    res = client.get("/api/v1/autores?skip=0&limit=5")
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert "total" in data
    assert data["limit"] == 5

