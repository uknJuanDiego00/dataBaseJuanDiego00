class ErrorAplicacion(Exception):
    """Clase base de todas las excepciones propias de la aplicación."""
    status_code: int = 400

    def __init__(self, mensaje: str = "Error en la aplicación"):
        super().__init__(mensaje)
        self.mensaje = mensaje


class NoEncontrado(ErrorAplicacion):
    """El recurso solicitado no existe."""
    status_code: int = 404

    def __init__(self, mensaje: str = "Recurso no encontrado"):
        super().__init__(mensaje)


class Conflicto(ErrorAplicacion):
    """Conflicto de integridad: datos duplicados o borrado con dependencias."""
    status_code: int = 409

    def __init__(self, mensaje: str = "Conflicto en la operación"):
        super().__init__(mensaje)


class ReglaNegocio(ErrorAplicacion):
    """Incumplimiento de una regla de negocio del sistema de biblioteca."""
    status_code: int = 422

    def __init__(self, mensaje: str = "Regla de negocio no cumplida"):
        super().__init__(mensaje)
