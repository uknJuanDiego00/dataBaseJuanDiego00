import cloudinary
import cloudinary.uploader
from fastapi import UploadFile
from ..core.config import settings
from ..core.exceptions import ReglaNegocio

# Formatos de imagen permitidos
FORMATOS_PERMITIDOS = {"image/jpeg", "image/png", "image/webp", "image/jpg"}
TAMANIO_MAXIMO_MB = 5
TAMANIO_MAXIMO_BYTES = TAMANIO_MAXIMO_MB * 1024 * 1024


def _configurar_cloudinary() -> None:
    """Configura el cliente de Cloudinary utilizando las variables de entorno."""
    if not (settings.CLOUDINARY_CLOUD_NAME and settings.CLOUDINARY_API_KEY and settings.CLOUDINARY_API_SECRET):
        raise ReglaNegocio(
            "Cloudinary no está configurado. Verifique CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY y CLOUDINARY_API_SECRET en el archivo .env"
        )

    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True
    )


def subir_imagen(archivo: UploadFile, carpeta: str = "biblioteca/libros") -> str:
    """Valida y sube un archivo de imagen a Cloudinary, retornando su URL segura."""
    _configurar_cloudinary()

    # Validar tipo de contenido
    if archivo.content_type not in FORMATOS_PERMITIDOS:
        raise ReglaNegocio(
            f"Tipo de archivo no permitido: {archivo.content_type}. Formatos aceptados: JPG, JPEG, PNG, WEBP"
        )

    try:
        # Subir a Cloudinary desde el stream del archivo
        resultado = cloudinary.uploader.upload(
            archivo.file,
            folder=carpeta,
            resource_type="image"
        )
        return resultado.get("secure_url", "")
    except Exception as e:
        if isinstance(e, ReglaNegocio):
            raise e
        raise ReglaNegocio(f"Error al subir imagen a Cloudinary: {str(e)}")

