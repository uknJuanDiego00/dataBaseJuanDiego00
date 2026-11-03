import pytest
from fastapi.testclient import TestClient


def test_caso_01_registro_password_invalida(client: TestClient):
    """Caso 1: Registro con contraseña inválida (sin número o mayúscula) -> 422."""
    res = client.post("/api/v1/auth/registro", json={
        "nombre": "Carlos Perez",
        "email": "carlos_invalido@test.com",
        "password": "sololetrasminusculas",
        "password_confirmacion": "sololetrasminusculas"
    })
    assert res.status_code == 422


def test_caso_02_confirmacion_password_diferente(client: TestClient):
    """Caso 2: Confirmación de contraseña diferente -> 422."""
    res = client.post("/api/v1/auth/registro", json={
        "nombre": "Carlos Perez",
        "email": "carlos_diff@test.com",
        "password": "Password123*",
        "password_confirmacion": "Password999*"
    })
    assert res.status_code == 422


def test_caso_03_registro_valido(client: TestClient):
    """Caso 3: Registro válido -> 201 con datos de usuario y socio creados."""
    res = client.post("/api/v1/auth/registro", json={
        "nombre": "Ana Morales",
        "email": "ana.morales@test.com",
        "password": "Password123*",
        "password_confirmacion": "Password123*",
        "telefono": "+57 3001122334"
    })
    assert res.status_code == 201
    data = res.json()
    assert data["email"] == "ana.morales@test.com"
    assert data["rol"] == "socio"
    assert data["activo"] is True
    assert data["socio_id"] is not None
    assert "password" not in data
    assert "password_hash" not in data


def test_caso_04_email_duplicado_case_insensitive(client: TestClient):
    """Caso 4: Email duplicado ignorando mayúsculas -> 409."""
    res = client.post("/api/v1/auth/registro", json={
        "nombre": "Ana Morales Copia",
        "email": "ANA.MORALES@TEST.COM",
        "password": "Password123*",
        "password_confirmacion": "Password123*"
    })
    assert res.status_code == 409


def test_caso_05_login_incorrecto_password(client: TestClient):
    """Caso 5: Login con contraseña incorrecta -> 401."""
    res = client.post("/api/v1/auth/login", data={
        "username": "ana.morales@test.com",
        "password": "PasswordEquivocada123*"
    })
    assert res.status_code == 401
    assert "detail" in res.json()


def test_caso_06_email_inexistente_mismo_mensaje(client: TestClient):
    """Caso 6: Email inexistente con el mismo mensaje genérico -> 401."""
    res_inexistente = client.post("/api/v1/auth/login", data={
        "username": "no_existe_usuario_jamais@test.com",
        "password": "CualquierPassword123*"
    })
    res_bad_pw = client.post("/api/v1/auth/login", data={
        "username": "ana.morales@test.com",
        "password": "PasswordEquivocada123*"
    })
    assert res_inexistente.status_code == 401
    assert res_bad_pw.status_code == 401
    # Mensaje uniforme para prevenir enumeración de usuarios
    assert res_inexistente.json()["detail"] == res_bad_pw.json()["detail"]


def test_caso_07_login_correcto(client: TestClient):
    """Caso 7: Login correcto -> 200 con access y refresh tokens."""
    res = client.post("/api/v1/auth/login", data={
        "username": "ana.morales@test.com",
        "password": "Password123*"
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"].lower() == "bearer"
    assert data["expires_in"] > 0


def test_caso_08_acceso_sin_token_cabecera_bearer(client: TestClient):
    """Caso 8: Acceso sin token a endpoint protegido -> 401 WWW-Authenticate: Bearer."""
    res = client.get("/api/v1/auth/me")
    assert res.status_code == 401
    assert "WWW-Authenticate" in res.headers
    assert "Bearer" in res.headers["WWW-Authenticate"]


def test_caso_09_token_alterado(client: TestClient):
    """Caso 9: Token alterado o con firma inválida -> 401."""
    res = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer token.alterado.invalido123"})
    assert res.status_code == 401


def test_caso_10_refresh_usado_como_access(client: TestClient, tokens_iniciales: dict):
    """Caso 10: Refresh token utilizado como access token -> 401."""
    refresh_token = tokens_iniciales["socio1_refresh"]
    res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {refresh_token}"})
    assert res.status_code == 401
    assert "tipo de token inválido" in res.json()["detail"].lower()


def test_caso_20_rotacion_refresh_tokens(client: TestClient):
    """Caso 20: Rotación de refresh tokens -> 200 y nuevo par de tokens."""
    login_res = client.post("/api/v1/auth/login", data={
        "username": "ana.morales@test.com",
        "password": "Password123*"
    })
    old_refresh = login_res.json()["refresh_token"]

    refresh_res = client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert refresh_res.status_code == 200
    new_data = refresh_res.json()
    assert "access_token" in new_data
    assert "refresh_token" in new_data
    assert new_data["refresh_token"] != old_refresh


def test_caso_21_reutilizacion_refresh_anterior(client: TestClient):
    """Caso 21: Reutilización de refresh token anterior -> 401 y revocación de todos."""
    login_res = client.post("/api/v1/auth/login", data={
        "username": "ana.morales@test.com",
        "password": "Password123*"
    })
    token_1 = login_res.json()["refresh_token"]

    # 1era rotación válida
    rot_res = client.post("/api/v1/auth/refresh", json={"refresh_token": token_1})
    assert rot_res.status_code == 200
    token_2 = rot_res.json()["refresh_token"]

    # Reutilización de token_1 ya rotado
    reuso_res = client.post("/api/v1/auth/refresh", json={"refresh_token": token_1})
    assert reuso_res.status_code == 401

    # token_2 también debe haber sido revocado por detección de reutilización
    reuso_token_2 = client.post("/api/v1/auth/refresh", json={"refresh_token": token_2})
    assert reuso_token_2.status_code == 401


def test_caso_22_logout_y_revocacion(client: TestClient):
    """Caso 22: Logout y revocación -> 204 y token revocado no utilizable."""
    login_res = client.post("/api/v1/auth/login", data={
        "username": "ana.morales@test.com",
        "password": "Password123*"
    })
    ref_token = login_res.json()["refresh_token"]

    logout_res = client.post("/api/v1/auth/logout", json={"refresh_token": ref_token})
    assert logout_res.status_code == 204

    # Intentar usar el token cerrado
    post_logout_res = client.post("/api/v1/auth/refresh", json={"refresh_token": ref_token})
    assert post_logout_res.status_code == 401


def test_caso_23_bloqueo_cinco_intentos_fallidos(client: TestClient):
    """Caso 23: Bloqueo de cuenta tras cinco intentos fallidos consecutivos -> 423."""
    # Crear usuario exclusivo para test de bloqueo
    client.post("/api/v1/auth/registro", json={
        "nombre": "Usuario Bloqueo",
        "email": "bloqueo.test@test.com",
        "password": "Password123*",
        "password_confirmacion": "Password123*"
    })

    # 4 intentos fallidos
    for _ in range(4):
        r = client.post("/api/v1/auth/login", data={"username": "bloqueo.test@test.com", "password": "WrongPassword1*"})
        assert r.status_code == 401

    # 5to intento fallido activa bloqueo 423
    r5 = client.post("/api/v1/auth/login", data={"username": "bloqueo.test@test.com", "password": "WrongPassword1*"})
    assert r5.status_code == 423

    # Incluso con la contraseña correcta debe responder 423
    r_locked = client.post("/api/v1/auth/login", data={"username": "bloqueo.test@test.com", "password": "Password123*"})
    assert r_locked.status_code == 423

