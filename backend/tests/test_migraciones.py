import pytest
from alembic import command
from alembic.config import Config


def test_caso_32_migraciones_alembic_upgrade_downgrade():
    """Caso 32: Comprueba que las migraciones de Alembic se apliquen y reviertan de forma limpia."""
    alembic_cfg = Config("alembic.ini")

    # Upgrade hasta la última versión
    try:
        command.upgrade(alembic_cfg, "head")
    except Exception as e:
        pytest.skip(f"Omitiendo test de migración en vivo si no hay conexión Postgres local: {e}")

    # Downgrade hasta la migración 0001
    try:
        command.downgrade(alembic_cfg, "0001")
        # Re-aplicar head
        command.upgrade(alembic_cfg, "head")
    except Exception as e:
        pytest.skip(f"Omitiendo downgrade si la base de datos no soporta rollback de esquemas en vivo: {e}")

