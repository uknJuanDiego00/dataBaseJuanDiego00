from fastapi.testclient import TestClient


def test_caso_24_rate_limiting_login(client: TestClient):
    """Caso 24: Rate limiting en login - máximo 10 peticiones por minuto -> 429."""
    respuestas = []
    # Realizar más de 10 peticiones rápidas
    for _ in range(12):
        r = client.post("/api/v1/auth/login", data={
            "username": "rate_limit_test@test.com",
            "password": "Password123*"
        })
        respuestas.append(r.status_code)

    # Al menos la última petición debe haber retornado 429 Too Many Requests
    assert 429 in respuestas, f"Se esperaba 429 en las respuestas, pero se obtuvo: {respuestas}"


def test_rate_limiting_registro(client: TestClient):
    """Rate limiting en registro - máximo 5 peticiones por minuto -> 429."""
    respuestas = []
    for i in range(7):
        r = client.post("/api/v1/auth/registro", json={
            "nombre": f"Usuario Rate {i}",
            "email": f"rate_{i}@test.com",
            "password": "Password123*",
            "password_confirmacion": "Password123*"
        })
        respuestas.append(r.status_code)

    # Debe saltar el rate limit (429) tras superar 5
    assert 429 in respuestas, f"Se esperaba 429 en las respuestas, pero se obtuvo: {respuestas}"

