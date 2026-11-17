import getpass
import sys
from sqlalchemy import func, select

from app.core.database import SessionLocal
from app.core.security import get_password_hash, validar_complejidad_password
from app.models.usuario import RolUsuario, Usuario


def crear_primer_admin() -> None:
    """Script interactivo de consola para crear el primer usuario administrador."""
    print("=" * 60)
    print(" CREACIÓN DEL USUARIO ADMINISTRADOR INICIAL")
    print("=" * 60)

    db = SessionLocal()
    try:
        # Verificar si ya existe un administrador
        admin_existente = db.scalar(
            select(Usuario).where(Usuario.rol == RolUsuario.admin)
        )
        if admin_existente:
            print(f"[!] Ya existe al menos un usuario administrador: {admin_existente.email}")
            respuesta = input("¿Desea crear otro administrador adicional? (s/n): ").strip().lower()
            if respuesta != "s":
                print("Operación cancelada.")
                return

        # Solicitar datos al usuario
        while True:
            email = input("Correo electrónico del administrador: ").strip().lower()
            if not email or "@" not in email:
                print("[-] Ingrese un correo electrónico válido.")
                continue
            # Comprobar unicidad
            duplicado = db.scalar(
                select(Usuario).where(func.lower(Usuario.email) == email)
            )
            if duplicado:
                print(f"[-] El correo {email} ya se encuentra registrado.")
                continue
            break

        while True:
            nombre = input("Nombre completo: ").strip()
            if len(nombre) < 2:
                print("[-] El nombre debe tener al menos 2 caracteres.")
                continue
            nombre = nombre.title()
            break

        while True:
            password = getpass.getpass("Contraseña: ")
            try:
                validar_complejidad_password(password)
            except ValueError as e:
                print(f"[-] Contraseña inválida: {e}")
                continue

            password_confirmacion = getpass.getpass("Confirme la contraseña: ")
            if password != password_confirmacion:
                print("[-] Las contraseñas no coinciden. Intente de nuevo.")
                continue
            break

        # Hashear con Argon2 y guardar
        hash_argon2 = get_password_hash(password)
        nuevo_admin = Usuario(
            email=email,
            nombre=nombre,
            password_hash=hash_argon2,
            rol=RolUsuario.admin,
            activo=True
        )
        db.add(nuevo_admin)
        db.commit()
        db.refresh(nuevo_admin)

        print("\n[+] ¡Usuario administrador creado exitosamente!")
        print(f"    ID:     {nuevo_admin.id}")
        print(f"    Email:  {nuevo_admin.email}")
        print(f"    Nombre: {nuevo_admin.nombre}")
        print(f"    Rol:    {nuevo_admin.rol.value}")

    except Exception as e:
        db.rollback()
        print(f"\n[-] Error al crear el administrador: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    crear_primer_admin()

