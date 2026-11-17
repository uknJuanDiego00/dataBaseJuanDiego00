"""Alembic environment configuration — importa todos los modelos para que
target_metadata los detecte automáticamente."""

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# -----------------------------------------------------------------------
# Carga de configuración centralizada
# -----------------------------------------------------------------------
import sys
import os

# Asegurar que el paquete app sea importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import get_settings
from app.core.database import Base

# Importar TODOS los modelos para que sus tablas aparezcan en Base.metadata
import app.models.autor          # noqa: F401
import app.models.categoria      # noqa: F401
import app.models.libro          # noqa: F401
import app.models.socio          # noqa: F401
import app.models.prestamo       # noqa: F401
import app.models.usuario        # noqa: F401
import app.models.refresh_token  # noqa: F401

settings = get_settings()

# -----------------------------------------------------------------------
# Alembic Config object
# -----------------------------------------------------------------------
config = context.config

# Sobrescribir sqlalchemy.url con el valor del settings (sin hardcodear)
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Configurar logging desde alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


# -----------------------------------------------------------------------
# Modo offline (genera SQL sin conexión real)
# -----------------------------------------------------------------------
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


# -----------------------------------------------------------------------
# Modo online (conexión real a la base de datos)
# -----------------------------------------------------------------------
def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

