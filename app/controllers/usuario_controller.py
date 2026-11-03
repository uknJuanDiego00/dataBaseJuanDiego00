from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from ..core.exceptions import Conflicto, NoEncontrado, ReglaNegocio
from ..core.security import get_password_hash
from ..models.refresh_token import RefreshToken
from ..models.usuario import RolUsuario, Usuario
from ..schemas.pagina import Pagina
from ..schemas.usuario import UsuarioActualizarActivo, UsuarioActualizarRol, UsuarioCrear, UsuarioRespuesta


def listar_usuarios(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    rol: RolUsuario | None = None,
    activo: bool | None = None
) -> Pagina[UsuarioRespuesta]:
    """Lista paginada de usuarios con filtros por rol y estado activo."""
    consulta = select(Usuario)

    if rol is not None:
        consulta = consulta.where(Usuario.rol == rol)
    if activo is not None:
        consulta = consulta.where(Usuario.activo == activo)

    # Conteo total con la misma consulta filtrada
    conteo_query = select(func.count()).select_from(consulta.subquery())
    total = db.scalar(conteo_query) or 0

    items = list(db.scalars(consulta.order_by(Usuario.id).offset(skip).limit(limit)).all())
    items_schemas = [UsuarioRespuesta.model_validate(u) for u in items]

    return Pagina[UsuarioRespuesta](
        items=items_schemas,
        total=total,
        skip=skip,
        limit=limit
    )


def obtener_usuario(db: Session, usuario_id: int) -> Usuario:
    """Obtiene un usuario por ID o lanza 404."""
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise NoEncontrado("Usuario no encontrado")
    return usuario


def crear_usuario(db: Session, datos: UsuarioCrear) -> Usuario:
    """Crea un usuario por parte del administrador."""
    email_limpio = datos.email.strip().lower()

    existente = db.scalar(
        select(Usuario).where(func.lower(Usuario.email) == email_limpio)
    )
    if existente:
        raise Conflicto("El correo electrónico ya está registrado")

    usuario = Usuario(
        email=email_limpio,
        nombre=datos.nombre,
        password_hash=get_password_hash(datos.password),
        rol=datos.rol,
        activo=True
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def cambiar_rol(
    db: Session,
    usuario_id: int,
    datos: UsuarioActualizarRol,
    admin_autenticado: Usuario
) -> Usuario:
    """
    Actualiza el rol de un usuario.
    Regla Z5: Protección del último administrador activo.
    Regla Z6: Revocación de refresh tokens al cambiar rol.
    """
    usuario = obtener_usuario(db, usuario_id)

    # Si es admin y se le quiere cambiar el rol, verificar que no sea el último admin activo
    if usuario.rol == RolUsuario.admin and datos.rol != RolUsuario.admin:
        # Si es él mismo
        if usuario.id == admin_autenticado.id:
            raise ReglaNegocio("Un administrador no puede quitarse su propio rol de administrador")

        total_admins = db.scalar(
            select(func.count(Usuario.id)).where(
                Usuario.rol == RolUsuario.admin,
                Usuario.activo == True
            )
        ) or 0
        if total_admins <= 1:
            raise ReglaNegocio("No se puede degradar al único administrador activo del sistema")

    usuario.rol = datos.rol

    # Regla Z6: Revocar todos los refresh tokens
    db.execute(
        update(RefreshToken)
        .where(RefreshToken.usuario_id == usuario.id)
        .values(revocado=True)
    )
    db.commit()
    db.refresh(usuario)
    return usuario


def cambiar_activo(
    db: Session,
    usuario_id: int,
    datos: UsuarioActualizarActivo,
    admin_autenticado: Usuario
) -> Usuario:
    """
    Activa o desactiva a un usuario.
    Regla Z5: No desactivar al último admin activo ni a sí mismo.
    Regla Z6: Revocar todos los refresh tokens al desactivar.
    """
    usuario = obtener_usuario(db, usuario_id)

    if usuario.rol == RolUsuario.admin and not datos.activo:
        if usuario.id == admin_autenticado.id:
            raise ReglaNegocio("Un administrador no puede desactivarse a sí mismo")

        total_admins = db.scalar(
            select(func.count(Usuario.id)).where(
                Usuario.rol == RolUsuario.admin,
                Usuario.activo == True
            )
        ) or 0
        if total_admins <= 1:
            raise ReglaNegocio("No se puede desactivar al único administrador activo del sistema")

    usuario.activo = datos.activo

    # Regla Z6: Si se desactiva, revocar todos los refresh tokens
    if not datos.activo:
        db.execute(
            update(RefreshToken)
            .where(RefreshToken.usuario_id == usuario.id)
            .values(revocado=True)
        )

    db.commit()
    db.refresh(usuario)
    return usuario

