import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Cargar variables de entorno desde el archivo .env
load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:1234@localhost:5432/biblioteca"
)

# Motor de conexión a PostgreSQL
engine = create_engine(
    DATABASE_URL,
    echo=False
)

# Fábrica de sesiones
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False
)


# Clase Base para modelos declarativos de SQLAlchemy
class Base(DeclarativeBase):
    pass
