# API REST Segura con FastAPI – Taller 2: Biblioteca SENA

Sistema backend robusto, modular y seguro para la administración integral de una biblioteca pública desarrollado con **Python 3.13**, **FastAPI**, **SQLAlchemy 2.0**, **PostgreSQL**, **Alembic**, **PyJWT**, **Argon2 (pwdlib)** y **SlowAPI**.

El proyecto implementa el patrón **MVC** con estricta separación de responsabilidades, control de acceso basado en roles (**RBAC**), control estricto de propiedad de recursos, rotación y revocación de tokens de refresco, protección contra fuerza bruta y migración de esquemas y datos versionados.

---

## 🏛️ Arquitectura del Sistema (Patrón MVC)

```text
biblioteca/
├── app/
│   ├── main.py                     # Inicializa FastAPI, middlewares (CORS, Limiter, Request-ID, Error 500) y routers
│   ├── core/
│   │   ├── config.py               # Configuración centralizada pydantic-settings y lectura de .env
│   │   ├── database.py             # Engine SQLAlchemy, SessionLocal y Base declarativa con NAMING_CONVENTION
│   │   ├── security.py             # Hasher Argon2 (pwdlib), validación de contraseñas y PyJWT
│   │   ├── dependencies.py         # Inyección de dependencias (DB, paginación, OAuth2 Bearer, requiere_rol)
│   │   └── exceptions.py           # Jerarquía de excepciones (400, 401, 403, 404, 409, 422, 423)
│   ├── models/
│   │   ├── autor.py                # Modelo ORM autores
│   │   ├── categoria.py            # Modelo ORM categorias
│   │   ├── libro.py                # Modelo ORM libros y tabla intermedia libro_categoria
│   │   ├── socio.py                # Modelo ORM socios (relación 1:1 con Usuario)
│   │   ├── prestamo.py             # Modelo ORM prestamos (multa_pagada y registrado_por_id)
│   │   ├── usuario.py              # Modelo ORM usuarios y Enum RolUsuario (admin, bibliotecario, socio)
│   │   └── refresh_token.py        # Modelo ORM refresh_tokens para rotación y revocación
│   ├── schemas/
│   │   ├── auth.py                 # Esquemas para login, refresh, registro y cambio de password
│   │   ├── usuario.py              # Esquemas para administración de usuarios y roles
│   │   ├── pagina.py               # Esquema genérico Pagina[T] con items, total, skip, limit
│   │   ├── autor.py                # Esquemas y validadores de autores
│   │   ├── categoria.py            # Esquemas y validadores de categorías
│   │   ├── libro.py                # Esquemas, filtros y ordenamiento de libros
│   │   ├── socio.py                # Esquemas y validadores de socios (incluye SocioMeActualizar)
│   │   ├── prestamo.py             # Esquemas de préstamos, multas y devoluciones
│   │   └── reporte.py              # Esquemas de respuesta para los reportes analíticos
│   ├── controllers/
│   │   ├── auth_controller.py      # Login OAuth2, refresh rotativo, logout, bloqueo por intentos
│   │   ├── usuario_controller.py   # Gestión de usuarios, cambio de roles, protección último admin
│   │   ├── autor_controller.py     # Lógica y consultas paginadas de autores
│   │   ├── categoria_controller.py # Lógica y consultas de categorías
│   │   ├── libro_controller.py     # Filtros combinables, cálculo de disponibles y paginación
│   │   ├── socio_controller.py     # Lógica de socios, endpoints /me, préstamos y multas propias
│   │   ├── prestamo_controller.py  # Reglas R1-R11, pago de multas, auditoría bibliotecario
│   │   └── reporte_controller.py   # Consultas analíticas en SQL puro
│   ├── routes/
│   │   ├── auth_router.py          # Endpoints /api/v1/auth (login, refresh, logout, me, registro)
│   │   ├── usuario_router.py       # Endpoints /api/v1/usuarios (solo Admin)
│   │   ├── health_router.py        # Endpoint /api/v1/health (200 o 503)
│   │   ├── autor_router.py         # Endpoints /api/v1/autores
│   │   ├── categoria_router.py     # Endpoints /api/v1/categorias
│   │   ├── libro_router.py         # Endpoints /api/v1/libros
│   │   ├── socio_router.py         # Endpoints /api/v1/socios y /api/v1/socios/me
│   │   ├── prestamo_router.py      # Endpoints /api/v1/prestamos y /pago-multa
│   │   └── reporte_router.py       # Endpoints /api/v1/reportes (Bibliotecario y Admin)
│   └── scripts/
│       └── crear_admin.py          # Script interactivo de consola con getpass para crear admin inicial
├── alembic/
│   ├── env.py                      # Conexión de Alembic con get_settings() y Base.metadata
│   └── versions/
│       ├── 0001_estado_inicial.py  # Tablas base del Taller 1
│       ├── 0002_multa_pagada.py    # Columna multa_pagada y migración de datos
│       ├── 0003_usuarios.py        # Tabla usuarios, Enum rolusuario y relación 1:1 con socios
│       ├── 0004_refresh_tokens.py  # Tabla refresh_tokens con jti y revocación
│       └── 0005_auditoria_prestamos.py # FK registrado_por_id en prestamos
├── tests/
│   ├── conftest.py                 # Fixtures, base de pruebas y tokens JWT iniciales
│   ├── test_auth.py                # Pruebas de registro, login, refresh, rotación, bloqueo 423
│   ├── test_roles.py               # Matriz de roles (RBAC), catálogo público, protección último admin
│   ├── test_prestamos_seguridad.py # Regla R11, propiedad de recursos (404 ajenos), pago de multa
│   ├── test_usuarios.py            # Endpoints administrativos de usuarios
│   ├── test_paginacion.py          # Paginación Pagina[T] con items, total, skip, limit
│   ├── test_rate_limit.py          # SlowAPI rate limiting (429)
│   ├── test_health.py              # GET /api/v1/health con comprobación de BD
│   ├── test_migraciones.py         # Upgrade y downgrade de Alembic
│   └── test_taller.py              # Suite de compatibilidad con los 24 casos originales
├── alembic.ini                     # Archivo de configuración principal de Alembic
├── Dockerfile                      # Imagen multi-stage en Python 3.13 slim
├── docker-compose.yml              # Orquestación con PostgreSQL 16 y FastAPI
├── requirements.txt                # Dependencias de producción
├── requirements-dev.txt            # Dependencias de pruebas y análisis
├── .env.example                    # Plantilla de variables de entorno
└── README.md                       # Documentación técnica completa
```

---

## 🔐 Matriz de Permisos y Roles (RBAC)

| Módulo / Endpoint | Anónimo | Socio | Bibliotecario | Administrador |
| :--- | :---: | :---: | :---: | :---: |
| `GET /api/v1/health` | ✅ | ✅ | ✅ | ✅ |
| `POST /api/v1/auth/registro` | ✅ | ❌ | ❌ | ❌ |
| `POST /api/v1/auth/login` | ✅ | ✅ | ✅ | ✅ |
| `POST /api/v1/auth/refresh` | ✅ | ✅ | ✅ | ✅ |
| `POST /api/v1/auth/logout` | ❌ | ✅ | ✅ | ✅ |
| `GET /api/v1/auth/me` | ❌ | ✅ | ✅ | ✅ |
| `PATCH /api/v1/auth/me/password` | ❌ | ✅ | ✅ | ✅ |
| `GET /api/v1/libros`, `GET /api/v1/libros/{id}` | ✅ | ✅ | ✅ | ✅ |
| `POST /api/v1/libros`, `PATCH /api/v1/libros/{id}` | ❌ | ❌ | ✅ | ✅ |
| `DELETE /api/v1/libros/{id}` | ❌ | ❌ | ❌ | ✅ |
| `GET /api/v1/autores`, `GET /api/v1/categorias` | ✅ | ✅ | ✅ | ✅ |
| `POST / PATCH` Autores y Categorías | ❌ | ❌ | ✅ | ✅ |
| `DELETE` Autores y Categorías | ❌ | ❌ | ❌ | ✅ |
| `GET /api/v1/socios/me`, `PATCH /api/v1/socios/me` | ❌ | ✅ | ❌ | ❌ |
| `GET /api/v1/socios/me/prestamos`, `.../multas` | ❌ | ✅ | ❌ | ❌ |
| `GET /api/v1/socios`, `POST / PATCH` Socios | ❌ | ❌ | ✅ | ✅ |
| `DELETE /api/v1/socios/{id}` | ❌ | ❌ | ❌ | ✅ |
| `GET /api/v1/prestamos` | ❌ | Solo propios | Todos | Todos |
| `GET /api/v1/prestamos/{id}` | ❌ | Solo propio (404 si ajeno) | Cualquiera | Cualquiera |
| `POST /api/v1/prestamos` (Registrar) | ❌ | ❌ | ✅ (auditoría) | ✅ (auditoría) |
| `POST /api/v1/prestamos/{id}/devolucion` | ❌ | ❌ | ✅ | ✅ |
| `POST /api/v1/prestamos/{id}/pago-multa` | ❌ | Propio | ✅ | ✅ |
| `GET /api/v1/reportes/*` | ❌ | ❌ | ✅ | ✅ |
| `GET /api/v1/usuarios`, `POST /api/v1/usuarios` | ❌ | ❌ | ❌ | ✅ |
| `PATCH /api/v1/usuarios/{id}/rol` o `/activo` | ❌ | ❌ | ❌ | ✅ |

---

## 🛡️ Reglas de Seguridad y Negocio Implementadas

1. **R1 a R8 (Préstamos):**
   - Socio existente (404), Libro existente (404), Socio activo (422).
   - **R11 (Regla nueva):** El socio no puede tener multas pendientes de pago (422 `"El socio tiene multas pendientes"`).
   - Socio sin préstamos vencidos (422).
   - Máximo de 3 préstamos sin devolver (422).
   - No duplicar préstamo del mismo libro sin devolver (409).
   - Ejemplares físicos disponibles en inventario (422).
   - Fecha límite calculada: `fecha_prestamo + dias` (1 a 30 días, defecto 14).
2. **R9 y R10 (Devoluciones y Multas):**
   - Validación de existencia y no devuelto previamente.
   - Cálculo de multa: retraso en días $\times \$0.50$ con `multa_pagada = False`. A tiempo: multa $\$0.00$ con `multa_pagada = True`.
3. **Z1 a Z7 (Seguridad y Autorización):**
   - **Z1:** Acceso restringido por roles según matriz RBAC (`requiere_rol`).
   - **Z2:** Un socio que consulte un préstamo ajeno recibe **404 NoEncontrado**.
   - **Z3:** Consultas de préstamos por socios se filtran forzosamente por su `socio_id`.
   - **Z4:** El socio solo puede actualizar nombre y teléfono; email, rol y estado activo están blindados.
   - **Z5:** Protección del último administrador activo (no puede degradarse ni desactivarse a sí mismo).
   - **Z6:** Cambiar rol o desactivar a un usuario revoca inmediatamente todos sus refresh tokens.
   - **Z7:** Auditoría en préstamos registrando el bibliotecario responsable (`registrado_por_id`).
4. **Protección contra Fuerza Bruta:**
   - Bloqueo temporal por **15 minutos** tras **5 intentos fallidos consecutivos** (código HTTP **423 Locked**).
   - Mensajes uniformes para evitar enumeración de usuarios.
5. **Rotación y Revocación de Tokens:**
   - Detección de reutilización de refresh tokens revocados: revoca automáticamente toda la sesión del usuario.

---

## 🚀 Instalación y Puesta en Marcha

### 1. Clonar el repositorio y preparar entorno virtual
```bash
git clone <url-del-repositorio>
cd dataBaseJuanDiego00

# Crear entorno virtual con Python 3.13
python -m venv .venv

# Activar en Windows:
.venv\Scripts\activate
# Activar en Linux/macOS:
source .venv/bin/activate
```

### 2. Instalar dependencias
```bash
pip install --upgrade pip
pip install -r requirements.txt -r requirements-dev.txt
```

### 3. Configurar variables de entorno
Copie `.env.example` a `.env` y ajuste sus credenciales:
```bash
cp .env.example .env
```
Verifique que `SECRET_KEY` tenga al menos 32 caracteres y configure las cadenas de conexión PostgreSQL:
```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/biblioteca
TEST_DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/biblioteca_test
SECRET_KEY=48ab24b81be29e8aeed03ede90c7a4e1f58ee24d3ef11447deffd3282175cfe1
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
ENVIRONMENT=development
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173","http://localhost:8000"]
```

### 4. Ejecutar migraciones con Alembic
```bash
alembic upgrade head
```

### 5. Crear el usuario Administrador inicial
Ejecute el script interactivo por consola (solicita datos y contraseña oculta):
```bash
python -m app.scripts.crear_admin
```

### 6. Iniciar el servidor de desarrollo
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
- **Documentación interactiva Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Documentación alternativa ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Verificación de salud:** [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

---

## 🐳 Ejecución con Docker y Docker Compose

Para desplegar la aplicación completa con su base de datos PostgreSQL en contenedores:
```bash
docker compose up -d --build
```
El contenedor de la base de datos levantará con healthcheck activo; una vez saludable, la API ejecutará `alembic upgrade head` automáticamente e iniciará en el puerto `8000`.

---

## 🧪 Ejecución de Pruebas Automatizadas

La suite incluye los **33 casos de prueba de seguridad, JWT, RBAC y migraciones del Taller 2**, además de la suite de compatibilidad del Taller 1.

```bash
# Ejecutar todas las pruebas
pytest

# Ejecutar con reporte de cobertura
pytest --cov=app --cov-report=term-missing
```

---

## 👥 Integrantes del Proyecto
- **Aprendiz / Desarrollador:** Juan Diego Gómez
- **Programa:** Análisis y Desarrollo de Software (ADSO) – SENA
- **Taller 2:** API REST Segura con FastAPI: Autenticación, Autorización y Migraciones
