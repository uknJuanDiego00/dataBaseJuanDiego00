from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from .config import settings

# Convención de nombres para restricciones e índices compatible con Alembic
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=NAMING_CONVENTION)


# Clase Base para modelos declarativos de SQLAlchemy
class Base(DeclarativeBase):
    metadata = metadata


# Motor de conexión a PostgreSQL
engine = create_engine(
    settings.DATABASE_URL,
    echo=False
)

# Fábrica de sesiones
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False
)
