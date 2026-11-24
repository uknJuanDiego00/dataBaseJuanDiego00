import pytest
from fastapi.testclient import TestClient


def test_caso_11_catalogo_publico_paginado(client: TestClient):
    """Caso 11: Catálogo de libros accesible sin token con estructura Pagina[T]."""
    res = client.get("/api/v1/libros?skip=0&limit=5")
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert "total" in data
    assert "skip" in data
    assert "limit" in data
    assert isinstance(data["items"], list)


def test_caso_12_socio_intentando_crear_libro(client: TestClient, tokens_iniciales: dict):
    """Caso 12: Socio intentando crear libros -> 403 Prohibido."""
    socio_token = tokens_iniciales["socio1"]
    res = client.post(
        "/api/v1/libros",
        headers={"Authorization": f"Bearer {socio_token}"},
        json={
            "titulo": "Libro Prohibido",
            "isbn": "9781111111111",
            "anio_publicacion": 2020,
            "ejemplares": 3,
            "autor_id": 1,
            "categoria_ids": [1]
        }
    )
    assert res.status_code == 403


def test_caso_13_bibliotecario_creando_libro(client: TestClient, tokens_iniciales: dict):
    """Caso 13: Bibliotecario creando libros -> 201 Creado."""
    biblio_token = tokens_iniciales["biblio"]
    admin_token = tokens_iniciales["admin"]

    # Crear autor y categoría previos si no existen
    client.post("/api/v1/autores", headers={"Authorization": f"Bearer {admin_token}"}, json={
        "nombre": "Gabriel García Márquez", "nacionalidad": "Colombiana", "anio_nacimiento": 1927
    })
    client.post("/api/v1/categorias", headers={"Authorization": f"Bearer {admin_token}"}, json={
        "nombre": "realismo magico", "descripcion": "Novelas"
    })

    res = client.post(
        "/api/v1/libros",
        headers={"Authorization": f"Bearer {biblio_token}"},
        json={
            "titulo": "Cien Años de Soledad",
            "isbn": "9780307474728",
            "anio_publicacion": 1967,
            "ejemplares": 5,
            "autor_id": 1,
            "categoria_ids": [1]
        }
    )
    assert res.status_code in (201, 409)  # 201 creado o 409 si ya existía


def test_caso_14_bibliotecario_intentando_eliminar_libro(client: TestClient, tokens_iniciales: dict):
    """Caso 14: Bibliotecario intentando eliminar libros -> 403 (Solo Admin)."""
    biblio_token = tokens_iniciales["biblio"]
    res = client.delete(
        "/api/v1/libros/1",
        headers={"Authorization": f"Bearer {biblio_token}"}
    )
    assert res.status_code == 403


def test_caso_19_modificacion_prohibida_perfil_socio(client: TestClient, tokens_iniciales: dict):
    """Caso 19: Socio no puede modificar email, rol ni activo mediante PATCH /socios/me (Regla Z4)."""
    socio_token = tokens_iniciales["socio1"]

    # Intentar actualizar pasando campos prohibidos; el esquema SocioMeActualizar solo acepta nombre y telefono
    res = client.patch(
        "/api/v1/socios/me",
        headers={"Authorization": f"Bearer {socio_token}"},
        json={
            "nombre": "Socio Nombre Actualizado",
            "email": "hack_email@test.com",
            "rol": "admin",
            "activo": False
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert data["nombre"] == "Socio Nombre Actualizado"
    # El email debe permanecer intacto
    assert data["email"] == "socio1@biblioteca.test"
    assert data["activo"] is True


def test_caso_25_desactivacion_usuario_y_revocacion(client: TestClient, tokens_iniciales: dict):
    """Caso 25: Admin desactiva usuario -> 200 y revoca sus refresh tokens."""
    admin_token = tokens_iniciales["admin"]

    # Crear usuario temporal
    u_res = client.post("/api/v1/auth/registro", json={
        "nombre": "Usuario Desactivar",
        "email": "desactivar@test.com",
        "password": "Password123*",
        "password_confirmacion": "Password123*"
    })
    uid = u_res.json()["id"]

    login_temp = client.post("/api/v1/auth/login", data={"username": "desactivar@test.com", "password": "Password123*"})
    refresh_temp = login_temp.json()["refresh_token"]

    # Desactivar por admin
    desact_res = client.patch(
        f"/api/v1/usuarios/{uid}/activo",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"activo": False}
    )
    assert desact_res.status_code == 200
    assert desact_res.json()["activo"] is False

    # El refresh token debe estar revocado
    reuso_res = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_temp})
    assert reuso_res.status_code == 401


def test_caso_26_proteccion_ultimo_admin(client: TestClient, tokens_iniciales: dict):
    """Caso 26: Protección del último administrador activo -> 422."""
    admin_token = tokens_iniciales["admin"]

    # Obtener id del admin autenticado
    me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {admin_token}"})
    admin_id = me_res.json()["id"]

    # Intentar desactivarse a sí mismo
    desact_self = client.patch(
        f"/api/v1/usuarios/{admin_id}/activo",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"activo": False}
    )
    assert desact_self.status_code == 422

    # Intentar degradar su propio rol
    degradar_self = client.patch(
        f"/api/v1/usuarios/{admin_id}/rol",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"rol": "socio"}
    )
    assert degradar_self.status_code == 422


def test_caso_27_acceso_reportes_segun_roles(client: TestClient, tokens_iniciales: dict):
    """Caso 27: Reportes accesibles por Bibliotecario/Admin (200) y denegados a Socio/Anónimo (401/403)."""
    # Anónimo -> 401
    anon_res = client.get("/api/v1/reportes/resumen")
    assert anon_res.status_code == 401

    # Socio -> 403
    socio_token = tokens_iniciales["socio1"]
    socio_res = client.get("/api/v1/reportes/resumen", headers={"Authorization": f"Bearer {socio_token}"})
    assert socio_res.status_code == 403

    # Bibliotecario -> 200
    biblio_token = tokens_iniciales["biblio"]
    biblio_res = client.get("/api/v1/reportes/resumen", headers={"Authorization": f"Bearer {biblio_token}"})
    assert biblio_res.status_code == 200

    # Admin -> 200
    admin_token = tokens_iniciales["admin"]
    admin_res = client.get("/api/v1/reportes/resumen", headers={"Authorization": f"Bearer {admin_token}"})
    assert admin_res.status_code == 200

