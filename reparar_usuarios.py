
from sqlalchemy import text
from app.core.database import engine


def reparar_usuarios():
    with engine.begin() as connection:

        # Crear ENUM de roles si no existe
        connection.execute(text("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1
                    FROM pg_type
                    WHERE typname = 'rolusuario'
                ) THEN
                    CREATE TYPE rolusuario AS ENUM (
                        'admin',
                        'bibliotecario',
                        'socio'
                    );
                END IF;
            END
            $$;
        """))

        # Crear tabla usuarios
        connection.execute(text("""
            CREATE TABLE usuarios (
                id SERIAL PRIMARY KEY,
                email VARCHAR(150) NOT NULL,
                nombre VARCHAR(100) NOT NULL,
                password_hash VARCHAR(256) NOT NULL,
                rol rolusuario NOT NULL DEFAULT 'socio',
                activo BOOLEAN NOT NULL DEFAULT TRUE,
                intentos_fallidos INTEGER NOT NULL DEFAULT 0,
                bloqueado_hasta TIMESTAMP WITH TIME ZONE,
                socio_id INTEGER,
                creado_en TIMESTAMP WITH TIME ZONE
                    NOT NULL DEFAULT NOW(),

                CONSTRAINT fk_usuarios_socio_id_socios
                    FOREIGN KEY (socio_id)
                    REFERENCES socios(id),

                CONSTRAINT uq_usuarios_email
                    UNIQUE (email),

                CONSTRAINT uq_usuarios_socio_id
                    UNIQUE (socio_id)
            );
        """))

        # Crear índice de email
        connection.execute(text("""
            CREATE UNIQUE INDEX ix_usuarios_email
            ON usuarios(email);
        """))

    print("Reparacion completada correctamente.")


if __name__ == "__main__":
    reparar_usuarios()
