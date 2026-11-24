"""
Script de inicialización y población completa para la Biblioteca Serenidad.
Crea usuarios de todos los roles (Admin, Bibliotecario, Socio), socios vinculados,
categorías, autores, libros y préstamos de ejemplo.
Ideal para bases de datos nuevas en Render o entornos locales.
"""

import os
import sys
from datetime import date, timedelta

# Asegurar path para ejecución directa
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.core.database import SessionLocal, Base, engine
from app.core.security import get_password_hash
from app.models.usuario import Usuario, RolUsuario
from app.models.socio import Socio
from app.models.categoria import Categoria
from app.models.autor import Autor
from app.models.libro import Libro
from app.models.prestamo import Prestamo


def poblar_sistema_completo(silent: bool = False):
    def log(msg):
        if not silent:
            print(msg)

    log("=" * 60)
    log(" INICIANDO POBLACIÓN DE DATOS DE SERENIDAD")
    log("=" * 60)

    # 1. Asegurar tablas creadas
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # ---------------------------------------------------------
        # 1. CATEGORÍAS
        # ---------------------------------------------------------
        categorias_datos = [
            ("Literatura y Ficción", "Obras maestras de la narrativa clásica y contemporánea universal."),
            ("Ciencia Ficción y Distopía", "Exploraciones del futuro, utopías tecnológicas y realidades alternativas."),
            ("Filosofía y Pensamiento", "Ensayos fundamentales sobre la existencia, la ética y el conocimiento."),
            ("Historia y Crónica", "Investigaciones históricas y memorias que documentan el devenir humano."),
            ("Poesía y Arte", "Lírica, estética y creaciones artísticas de diversas épocas.")
        ]

        categorias_creadas = {}
        for nombre, desc in categorias_datos:
            cat = db.query(Categoria).filter(Categoria.nombre == nombre).first()
            if not cat:
                cat = Categoria(nombre=nombre, descripcion=desc)
                db.add(cat)
                db.flush()
                log(f"[+] Categoría creada: {nombre}")
            categorias_creadas[nombre] = cat

        # ---------------------------------------------------------
        # 2. AUTORES
        # ---------------------------------------------------------
        autores_datos = [
            ("Gabriel García Márquez", "Colombiana", 1927),
            ("Jorge Luis Borges", "Argentina", 1899),
            ("Isabel Allende", "Chilena", 1942),
            ("George Orwell", "Británica", 1903),
            ("Franz Kafka", "Checa", 1883),
            ("Virginia Woolf", "Británica", 1882)
        ]

        autores_creados = {}
        for nombre, nac, anio in autores_datos:
            autor = db.query(Autor).filter(Autor.nombre == nombre).first()
            if not autor:
                autor = Autor(nombre=nombre, nacionalidad=nac, anio_nacimiento=anio)
                db.add(autor)
                db.flush()
                log(f"[+] Autor creado: {nombre}")
            autores_creados[nombre] = autor

        # ---------------------------------------------------------
        # 3. SOCIOS LECTORES (Fichas de socios)
        # ---------------------------------------------------------
        socios_datos = [
            ("Gabriel García Lector", "socio1@biblioteca.com", "3001234567"),
            ("Isabel Allende Lectora", "socio2@biblioteca.com", "3007654321"),
            ("Jorge Luis Lector", "socio3@biblioteca.com", "3004567890"),
            ("Virginia Woolf Lectora", "socio4@biblioteca.com", "3009876543")
        ]

        socios_creados = {}
        for nombre, email, tel in socios_datos:
            socio = db.query(Socio).filter(Socio.email == email).first()
            if not socio:
                socio = Socio(
                    nombre=nombre,
                    email=email,
                    telefono=tel,
                    activo=True,
                    fecha_alta=date.today() - timedelta(days=60)
                )
                db.add(socio)
                db.flush()
                log(f"[+] Socio creado: {nombre} ({email})")
            socios_creados[email] = socio

        # ---------------------------------------------------------
        # 4. USUARIOS DEL SISTEMA (Admin, Bibliotecarios, Socios)
        # ---------------------------------------------------------
        usuarios_datos = [
            # Administradores
            ("admin@biblioteca.com", "Administrador Principal", "Admin123*", RolUsuario.admin, None),
            ("admin2@biblioteca.com", "Coordinadora de Biblioteca", "Admin123*", RolUsuario.admin, None),
            # Bibliotecarios / Personal
            ("biblio@biblioteca.com", "Bibliotecario Jefe", "Biblio123*", RolUsuario.bibliotecario, None),
            ("catalogo@biblioteca.com", "Gestor de Catálogo", "Biblio123*", RolUsuario.bibliotecario, None),
            # Socios Lectores vinculados
            ("socio1@biblioteca.com", "Gabriel García Lector", "Socio123*", RolUsuario.socio, socios_creados.get("socio1@biblioteca.com")),
            ("socio2@biblioteca.com", "Isabel Allende Lectora", "Socio123*", RolUsuario.socio, socios_creados.get("socio2@biblioteca.com")),
            ("socio3@biblioteca.com", "Jorge Luis Lector", "Socio123*", RolUsuario.socio, socios_creados.get("socio3@biblioteca.com")),
            ("socio4@biblioteca.com", "Virginia Woolf Lectora", "Socio123*", RolUsuario.socio, socios_creados.get("socio4@biblioteca.com")),
        ]

        for email, nombre, pwd, rol, socio_ref in usuarios_datos:
            usr = db.query(Usuario).filter(Usuario.email == email).first()
            if not usr:
                usr = Usuario(
                    email=email,
                    nombre=nombre,
                    password_hash=get_password_hash(pwd),
                    rol=rol,
                    activo=True,
                    socio_id=socio_ref.id if socio_ref else None
                )
                db.add(usr)
                log(f"[+] Usuario creado: {nombre} <{email}> (Rol: {rol.value})")
            else:
                # Asegurar vinculación con socio si correspondiera
                if socio_ref and not usr.socio_id:
                    usr.socio_id = socio_ref.id

        db.flush()

        # ---------------------------------------------------------
        # 5. LIBROS
        # ---------------------------------------------------------
        libros_datos = [
            (
                "Cien años de soledad",
                "9780307474728",
                1967,
                "Gabriel García Márquez",
                ["Literatura y Ficción"],
                5,
                "https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&q=80&w=600"
            ),
            (
                "Ficciones",
                "9788420633121",
                1944,
                "Jorge Luis Borges",
                ["Literatura y Ficción", "Filosofía y Pensamiento"],
                4,
                "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&q=80&w=600"
            ),
            (
                "La casa de los espíritus",
                "9788401341991",
                1982,
                "Isabel Allende",
                ["Literatura y Ficción"],
                4,
                "https://images.unsplash.com/photo-1497633762265-9d179a990aa6?auto=format&fit=crop&q=80&w=600"
            ),
            (
                "1984",
                "9780451524935",
                1949,
                "George Orwell",
                ["Ciencia Ficción y Distopía", "Filosofía y Pensamiento"],
                6,
                "https://images.unsplash.com/photo-1532012164546-f432f2e3777f?auto=format&fit=crop&q=80&w=600"
            ),
            (
                "La metamorfosis",
                "9788420651361",
                1915,
                "Franz Kafka",
                ["Literatura y Ficción", "Filosofía y Pensamiento"],
                3,
                "https://images.unsplash.com/photo-1543002588-bfa74002ed7e?auto=format&fit=crop&q=80&w=600"
            ),
            (
                "Al faro",
                "9788420651989",
                1927,
                "Virginia Woolf",
                ["Literatura y Ficción", "Poesía y Arte"],
                4,
                "https://images.unsplash.com/photo-1495446815901-a7297e633e8d?auto=format&fit=crop&q=80&w=600"
            )
        ]

        libros_creados = {}
        for titulo, isbn, anio, autor_nombre, cat_nombres, ejemplares, url_img in libros_datos:
            libro = db.query(Libro).filter(Libro.isbn == isbn).first()
            autor_obj = autores_creados.get(autor_nombre)
            if not libro and autor_obj:
                libro = Libro(
                    titulo=titulo,
                    isbn=isbn,
                    anio_publicacion=anio,
                    ejemplares=ejemplares,
                    autor_id=autor_obj.id,
                    url_imagen=url_img,
                    portada_url=url_img
                )
                for cat_nombre in cat_nombres:
                    cat_obj = categorias_creadas.get(cat_nombre)
                    if cat_obj:
                        libro.categorias.append(cat_obj)

                db.add(libro)
                db.flush()
                log(f"[+] Libro creado: {titulo} ({isbn})")
            libros_creados[titulo] = libro

        # ---------------------------------------------------------
        # 6. PRÉSTAMOS DE EJEMPLO
        # ---------------------------------------------------------
        admin_usr = db.query(Usuario).filter(Usuario.rol == RolUsuario.admin).first()
        admin_id = admin_usr.id if admin_usr else 1

        socio1 = socios_creados.get("socio1@biblioteca.com")
        socio2 = socios_creados.get("socio2@biblioteca.com")
        libro1 = libros_creados.get("Cien años de soledad")
        libro2 = libros_creados.get("1984")
        libro3 = libros_creados.get("Ficciones")

        prestamos_existentes = db.query(Prestamo).count()
        if prestamos_existentes == 0 and socio1 and libro1:
            # Préstamo 1: Activo en curso
            p1 = Prestamo(
                libro_id=libro1.id,
                socio_id=socio1.id,
                fecha_prestamo=date.today() - timedelta(days=5),
                fecha_limite=date.today() + timedelta(days=9),
                registrado_por_id=admin_id
            )
            # Préstamo 2: Ya devuelto
            p2 = Prestamo(
                libro_id=libro2.id if libro2 else libro1.id,
                socio_id=socio2.id if socio2 else socio1.id,
                fecha_prestamo=date.today() - timedelta(days=20),
                fecha_limite=date.today() - timedelta(days=6),
                fecha_devolucion=date.today() - timedelta(days=7),
                registrado_por_id=admin_id
            )
            # Préstamo 3: En curso
            if libro3:
                p3 = Prestamo(
                    libro_id=libro3.id,
                    socio_id=socio1.id,
                    fecha_prestamo=date.today() - timedelta(days=2),
                    fecha_limite=date.today() + timedelta(days=12),
                    registrado_por_id=admin_id
                )
                db.add(p3)

            db.add(p1)
            db.add(p2)
            log("[+] Préstamos de muestra creados.")

        db.commit()
        log("\n" + "=" * 60)
        log(" ¡POBLACIÓN COMPLETA FINALIZADA CON ÉXITO!")
        log("=" * 60)
        log("Cuentas creadas para entrar al sistema:")
        log("  - Admin:         admin@biblioteca.com      (Clave: Admin123*)")
        log("  - Coordinadora:  admin2@biblioteca.com     (Clave: Admin123*)")
        log("  - Bibliotecario: biblio@biblioteca.com     (Clave: Biblio123*)")
        log("  - Personal:      catalogo@biblioteca.com   (Clave: Biblio123*)")
        log("  - Socio 1:       socio1@biblioteca.com     (Clave: Socio123*)")
        log("  - Socio 2:       socio2@biblioteca.com     (Clave: Socio123*)")
        log("=" * 60)

    except Exception as e:
        db.rollback()
        log(f"[-] Error en población de datos: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    poblar_sistema_completo()
