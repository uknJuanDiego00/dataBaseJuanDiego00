from fastapi.testclient import TestClient


def test_admin_listar_usuarios_paginado(client: TestClient, tokens_iniciales: dict):
    """Admin puede listar usuarios con estructura paginada Pagina[UsuarioRespuesta]."""
    admin_token = tokens_iniciales["admin"]
    res = client.get("/api/v1/usuarios?skip=0&limit=5", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= len(data["items"])


def test_socio_no_puede_listar_usuarios(client: TestClient, tokens_iniciales: dict):
    """Un socio no tiene permisos para listar usuarios -> 403."""
    socio_token = tokens_iniciales["socio1"]
    res = client.get("/api/v1/usuarios", headers={"Authorization": f"Bearer {socio_token}"})
    assert res.status_code == 403


def test_admin_crear_usuario(client: TestClient, tokens_iniciales: dict):
    """Admin crea un usuario bibliotecario exitosamente -> 201."""
    admin_token = tokens_iniciales["admin"]
    res = client.post(
        "/api/v1/usuarios",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "nombre": "Nuevo Bibliotecario",
            "email": "nuevo.biblio@test.com",
            "password": "Password123*",
            "password_confirmacion": "Password123*",
            "rol": "bibliotecario"
        }
    )
    assert res.status_code == 201
    data = res.json()
    assert data["rol"] == "bibliotecario"
    assert data["email"] == "nuevo.biblio@test.com"


def test_admin_cambiar_rol_usuario(client: TestClient, tokens_iniciales: dict):
    """Admin cambia el rol de un usuario -> 200."""
    admin_token = tokens_iniciales["admin"]

    # Crear usuario temporal
    crear_res = client.post(
        "/api/v1/usuarios",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "nombre": "Usuario Rol Temp",
            "email": "rol.temp@test.com",
            "password": "Password123*",
            "password_confirmacion": "Password123*",
            "rol": "socio"
        }
    )
    uid = crear_res.json()["id"]

    # Cambiar rol a bibliotecario
    patch_res = client.patch(
        f"/api/v1/usuarios/{uid}/rol",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"rol": "bibliotecario"}
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["rol"] == "bibliotecario"

