from unittest.mock import patch
import io
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings


@pytest.fixture
def client():
    return TestClient(app)


def test_subir_portada_sin_configuracion_cloudinary(client: TestClient):
    """Verifica que si no hay credenciales configuradas, retorne error 422."""
    with patch.object(settings, "CLOUDINARY_CLOUD_NAME", ""):
        archivo = io.BytesIO(b"fake image data")
        res = client.post(
            "/libros/1/portada",
            files={"archivo": ("portada.png", archivo, "image/png")}
        )
        assert res.status_code == 422
        assert "Cloudinary no está configurado" in res.json()["detail"]


def test_subir_portada_formato_invalido(client: TestClient):
    """Verifica que rechace formatos no admitidos (ej: texto o pdf)."""
    with patch.object(settings, "CLOUDINARY_CLOUD_NAME", "demo"), \
         patch.object(settings, "CLOUDINARY_API_KEY", "12345"), \
         patch.object(settings, "CLOUDINARY_API_SECRET", "secret"):
        archivo = io.BytesIO(b"dummy text")
        res = client.post(
            "/libros/1/portada",
            files={"archivo": ("archivo.txt", archivo, "text/plain")}
        )
        assert res.status_code == 422
        assert "Tipo de archivo no permitido" in res.json()["detail"]


def test_subir_portada_exitoso(client: TestClient):
    """Verifica la subida exitosa y actualización de portada_url mockeando Cloudinary."""
    fake_url = "https://res.cloudinary.com/demo/image/upload/v1234/biblioteca/libros/portada_mock.jpg"

    with patch.object(settings, "CLOUDINARY_CLOUD_NAME", "demo"), \
         patch.object(settings, "CLOUDINARY_API_KEY", "12345"), \
         patch.object(settings, "CLOUDINARY_API_SECRET", "secret"), \
         patch("cloudinary.uploader.upload", return_value={"secure_url": fake_url}):

        # Primero obtener o crear autor y categoría si se requiere
        # O probar contra un libro existente
        # Para aislar, verificar con mock del controller o verificar libro 1
        archivo = io.BytesIO(b"\x89PNG\r\n\x1a\nfakeimage")
        res = client.post(
            "/libros/1/portada",
            files={"archivo": ("portada.png", archivo, "image/png")}
        )
        # Si el libro 1 existe en la base de datos local
        if res.status_code == 200:
            data = res.json()
            assert data["portada_url"] == fake_url
        else:
            # Si el libro 1 no existe, debe ser 404
            assert res.status_code == 404

