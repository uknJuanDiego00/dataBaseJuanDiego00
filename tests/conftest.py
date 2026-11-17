import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.database import Base, get_db
from app.core.security import get_password_hash
from app.main import app
from app.models.usuario import RolUsuario, Usuario
from app.models.socio import Socio

# Usar TEST_DATABASE_URL si está disponible, o SQLite en memoria para tests si no hay postgres
# Pero como estamos en entorno PostgreSQL o TestClient:
test_engine = create_engine(settings.DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Inicializa la base de datos de pruebas recreando las tablas limpias."""
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield
    # Cleanup opcional


@pytest.fixture(scope="function")
def db_session():
    """Genera una sesión de base de datos aislada por prueba con rollback opcional."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="session")
def client():
    return TestClient(app)


@pytest.fixture(scope="session")
def tokens_iniciales(client: TestClient):
    """Crea usuarios admin, bibliotecario y socio para pruebas y obtiene sus tokens JWT."""
    db = TestingSessionLocal()
    try:
        # 1. Admin
        admin = db.query(Usuario).filter(Usuario.email == "admin@biblioteca.test").first()
        if not admin:
            admin = Usuario(
                email="admin@biblioteca.test",
                nombre="Administrador Principal",
                password_hash=get_password_hash("Admin123*"),
                rol=RolUsuario.admin,
                activo=True
            )
            db.add(admin)

        # 2. Bibliotecario
        biblio = db.query(Usuario).filter(Usuario.email == "biblio@biblioteca.test").first()
        if not biblio:
            biblio = Usuario(
                email="biblio@biblioteca.test",
                nombre="Bibliotecario Jefe",
                password_hash=get_password_hash("Biblio123*"),
                rol=RolUsuario.bibliotecario,
                activo=True
            )
            db.add(biblio)

        # 3. Socio 1
        socio_ent = db.query(Socio).filter(Socio.email == "socio1@biblioteca.test").first()
        if not socio_ent:
            socio_ent = Socio(
                nombre="Socio Uno",
                email="socio1@biblioteca.test",
                telefono="3001234567",
                activo=True
            )
            db.add(socio_ent)
            db.flush()

        socio_user = db.query(Usuario).filter(Usuario.email == "socio1@biblioteca.test").first()
        if not socio_user:
            socio_user = Usuario(
                email="socio1@biblioteca.test",
                nombre="Socio Uno",
                password_hash=get_password_hash("Socio123*"),
                rol=RolUsuario.socio,
                activo=True,
                socio_id=socio_ent.id
            )
            db.add(socio_user)

        # 4. Socio 2 (para pruebas de propiedad)
        socio2_ent = db.query(Socio).filter(Socio.email == "socio2@biblioteca.test").first()
        if not socio2_ent:
            socio2_ent = Socio(
                nombre="Socio Dos",
                email="socio2@biblioteca.test",
                telefono="3007654321",
                activo=True
            )
            db.add(socio2_ent)
            db.flush()

        socio2_user = db.query(Usuario).filter(Usuario.email == "socio2@biblioteca.test").first()
        if not socio2_user:
            socio2_user = Usuario(
                email="socio2@biblioteca.test",
                nombre="Socio Dos",
                password_hash=get_password_hash("Socio223*"),
                rol=RolUsuario.socio,
                activo=True,
                socio_id=socio2_ent.id
            )
            db.add(socio2_user)

        db.commit()

        # Login para obtener tokens
        res_admin = client.post("/api/v1/auth/login", data={"username": "admin@biblioteca.test", "password": "Admin123*"})
        res_biblio = client.post("/api/v1/auth/login", data={"username": "biblio@biblioteca.test", "password": "Biblio123*"})
        res_socio1 = client.post("/api/v1/auth/login", data={"username": "socio1@biblioteca.test", "password": "Socio123*"})
        res_socio2 = client.post("/api/v1/auth/login", data={"username": "socio2@biblioteca.test", "password": "Socio223*"})

        return {
            "admin": res_admin.json()["access_token"],
            "admin_refresh": res_admin.json()["refresh_token"],
            "biblio": res_biblio.json()["access_token"],
            "socio1": res_socio1.json()["access_token"],
            "socio1_refresh": res_socio1.json()["refresh_token"],
            "socio1_id": socio_ent.id,
            "socio2": res_socio2.json()["access_token"],
            "socio2_id": socio2_ent.id,
        }
    finally:
        db.close()

