# API REST Biblioteca – FastAPI, SQLAlchemy y PostgreSQL

Sistema backend completo para la administración y control de una biblioteca pública desarrollado con **Python 3.13**, **FastAPI**, **SQLAlchemy 2.0**, **Pydantic V2** y **PostgreSQL**. El proyecto implementa una arquitectura por capas basada en el patrón **MVC**, garantizando una estricta separación de responsabilidades, validaciones robustas de entrada/salida, persistencia relacional con joins y funciones de agregación en SQL, y cumplimiento de reglas de negocio para préstamos y devoluciones.

---

## 🏛️ Estructura del Proyecto (Patrón MVC)

```text
├── app/
│   ├── main.py                     # Inicializa FastAPI, registra routers y manejador de excepciones
│   ├── core/
│   │   ├── database.py             # Conexión exclusiva a PostgreSQL (engine, SessionLocal, Base)
│   │   ├── dependencies.py         # Inyección de dependencias (SessionDep, PaginacionDep)
│   │   └── exceptions.py           # Jerarquía de excepciones propias (ErrorAplicacion, NoEncontrado, Conflicto, ReglaNegocio)
│   ├── models/
│   │   ├── autor.py                # Modelo ORM autores
│   │   ├── categoria.py            # Modelo ORM categorias
│   │   ├── libro.py                # Modelo ORM libros y tabla intermedia libro_categoria
│   │   ├── socio.py                # Modelo ORM socios
│   │   └── prestamo.py             # Modelo ORM prestamos
│   ├── schemas/
│   │   ├── autor.py                # Esquemas Pydantic y validadores de autores
│   │   ├── categoria.py            # Esquemas Pydantic y validadores de categorías
│   │   ├── libro.py                # Esquemas Pydantic, cálculo de disponibles y ordenamiento
│   │   ├── socio.py                # Esquemas Pydantic y validadores de socios
│   │   ├── prestamo.py             # Esquemas Pydantic de préstamos y devoluciones
│   │   └── reporte.py              # Esquemas de respuesta para los 6 reportes analíticos
│   ├── controllers/
│   │   ├── autor_controller.py     # Lógica y consultas de autores
│   │   ├── categoria_controller.py # Lógica y consultas de categorías
│   │   ├── libro_controller.py     # Lógica, filtros combinables y disponibles de libros
│   │   ├── socio_controller.py     # Lógica, borrado lógico y préstamos por socio
│   │   ├── prestamo_controller.py  # Reglas R1-R10, validación de inventario y cálculo de multas
│   │   └── reporte_controller.py   # Consultas SQL individuales para reportes
│   └── routes/
│       ├── autor_router.py         # Endpoints REST para /autores
│       ├── categoria_router.py     # Endpoints REST para /categorias
│       ├── libro_router.py         # Endpoints REST para /libros
│       ├── socio_router.py         # Endpoints REST para /socios
│       ├── prestamo_router.py      # Endpoints REST para /prestamos
│       └── reporte_router.py       # Endpoints REST para /reportes
├── tests/
│   └── test_taller.py              # Suite de pruebas automatizada con los 24 casos de prueba
├── .env.example                    # Plantilla de variables de entorno
├── .gitignore                      # Exclusión de .env, .venv y __pycache__
├── requirements.txt                # Dependencias del proyecto
└── README.md                       # Documentación técnica
```

---

## ⚙️ Separación de Responsabilidades

| Capa | Qué hace | Qué NO hace |
| :--- | :--- | :--- |
| **`models`** | Define las tablas, columnas, restricciones y relaciones ORM. | No valida datos de entrada de la petición. |
| **`schemas`** | Valida datos entrantes con Pydantic y estructura las respuestas JSON. | No ejecuta consultas a la base de datos. |
| **`controllers`** | Ejecuta consultas SQL, aplica reglas de negocio y lanza excepciones propias. | No utiliza `HTTPException` ni códigos de estado HTTP. |
| **`routes`** | Recibe la petición HTTP, invoca al controlador y asigna `status_code` y `response_model`. | No escribe consultas SQL ni maneja lógica de negocio. |

---

## 📋 Reglas de Negocio Implementadas

### Préstamos (`POST /prestamos`) – Verificadas en orden estricto:
1. **R1:** El socio debe existir en la base de datos (`404 NoEncontrado`).
2. **R2:** El libro debe existir en el catálogo (`404 NoEncontrado`).
3. **R3:** El socio debe estar activo (`422 ReglaNegocio("El socio no está activo")`).
4. **R4:** El socio no debe tener préstamos vencidos sin devolver (`422 ReglaNegocio("El socio tiene préstamos vencidos")`).
5. **R5:** El socio debe tener menos de 3 préstamos activos sin devolver (`422 ReglaNegocio("Máximo de 3 préstamos")`).
6. **R6:** El socio no debe tener ya prestado ese mismo libro sin devolver (`409 Conflicto("El socio ya tiene este libro sin devolver")`).
7. **R7:** El libro debe tener ejemplares disponibles en inventario (`422 ReglaNegocio("No hay ejemplares disponibles")`).
8. **R8:** Se calcula automáticamente la fecha límite: `fecha_limite = fecha_prestamo + dias` (días entre 1 y 30, defecto 14).

### Devoluciones (`POST /prestamos/{id}/devolucion`):
9. **R9:** El préstamo debe existir (`404`), no debe haber sido devuelto con anterioridad (`409`) y la fecha de devolución no puede ser anterior a la de préstamo (`422`).
10. **R10:** Si se devuelve después de la fecha límite: `multa = días de retraso × 0.50`. Si se devuelve a tiempo, la multa es `0.00`.

---

## 📊 Reportes Analíticos (SQL Puro en una Sola Consulta)

1. `GET /reportes/libros-mas-prestados?limite=5`: Libro, autor y total de préstamos ordenados de mayor a menor (`join + group_by + count + order_by`).
2. `GET /reportes/categorias`: Total de libros por categoría, incluyendo aquellas con 0 libros (`outerjoin + group_by`).
3. `GET /reportes/prestamos-vencidos`: Detalle de préstamos vencidos no devueltos con cálculo de días de retraso (`join de 3 tablas + where`).
4. `GET /reportes/socios-con-multas`: Socios con multas acumuladas y conteo de préstamos multados (`group_by + sum + having`).
5. `GET /reportes/autores`: Estadísticas completas por autor: total de libros, ejemplares físicos y préstamos acumulados (`outerjoin + count(distinct)`).
6. `GET /reportes/resumen`: Cuadro de mando global de la biblioteca con totales de libros, ejemplares, prestados, socios activos, vencidos y multas (`select(func.count()) y func.sum`).

---

## 🚀 Instalación y Puesta en Marcha

### 1. Clonar el repositorio y preparar el entorno virtual
```bash
python -m venv .venv
# En Windows:
.venv\Scripts\activate
# En Linux/macOS:
source .venv/bin/activate
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno
Crear el archivo `.env` a partir de `.env.example`:
```env
DATABASE_URL=postgresql+psycopg://postgres:1234@localhost:5432/biblioteca
```

### 4. Iniciar la API
```bash
uvicorn app.main:app --reload
```
La aplicación creará automáticamente las tablas en PostgreSQL si no existen al iniciar.
- Documentación interactiva Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Documentación Redoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🧪 Ejecución de Pruebas

Para ejecutar la suite automatizada con los 24 casos de prueba especificados en el taller:
```bash
python -m pytest tests/test_taller.py -v
```

### Casos de prueba validados:
| # | Caso de Prueba | Resultado Obtenido |
| :--- | :--- | :--- |
| **1** | POST /autores con "Gabriel García Márquez" duplicado | 409 Conflicto |
| **2** | POST /libros con ISBN "123" | 422 Validación Pydantic |
| **3** | POST /libros con categoria_ids duplicadas `[1, 1]` | 422 Validación Pydantic |
| **4** | POST /libros con autor_id inexistente (99) | 404 NoEncontrado |
| **5** | GET /libros?categoria_id=2&orden=-anio | 200 Ordenado descendente por año |
| **6** | GET /libros?autor=gabriel | 200 Retorna 2 libros del autor |
| **7** | Préstamo del libro 2 al socio 1 | 201 Creado, estado activo |
| **8** | Préstamo del libro 2 al socio 2 sin ejemplares | 422 ReglaNegocio |
| **9** | GET /libros/2 | 200 disponibles: 0 |
| **10** | Préstamo del libro 1 con fecha pasada y vencida | 201 Creado, estado vencido |
| **11** | Préstamo al socio con préstamos vencidos | 422 ReglaNegocio |
| **12** | GET /reportes/prestamos-vencidos | 200 dias_retraso: 13 |
| **13** | Devolución de préstamo vencido con retraso | 200 OK, multa: 6.5 |
| **14** | Devolución repetida del mismo préstamo | 409 Conflicto |
| **15** | Cuarto préstamo simultáneo a un mismo socio | 422 Máximo de 3 préstamos |
| **16** | PATCH /libros/4 con ejemplares menores a préstamos activos | 422 ReglaNegocio |
| **17** | DELETE /autores/1 con libros asociados | 409 Conflicto |
| **18** | DELETE /libros/2 con préstamo activo | 409 Conflicto |
| **19** | DELETE /socios/2 con historial devuelto | 204 No Content, activo: false |
| **20** | Intento de préstamo a socio inactivo | 422 Socio no está activo |
| **21** | GET /reportes/categorias (categoría poesía) | 200 total_libros: 0 |
| **22** | GET /reportes/socios-con-multas | 200 Solo Luis Pérez con 6.5 |
| **23** | GET /reportes/libros-mas-prestados?limite=3 | 200 3 libros ordenados desc |
| **24** | Paginación `?skip=0&limit=2` y `?skip=2&limit=2` | 200 Sin elementos repetidos |
