from sqlmodel import Session, select

from models.libro import Libro
from models.prestamo import Prestamo


def obtener_prestamo_por_id(session: Session, prestamo_id: int) -> Prestamo | None:
    return session.get(Prestamo, prestamo_id)


def contar_prestamos_activos_socio(session: Session, socio_id: int) -> int:
    query = select(Prestamo).where(
        Prestamo.socio_id == socio_id,
        Prestamo.fecha_devolucion.is_(None),
    )
    return len(session.exec(query).all())


def listar_prestamos_socio(
    session: Session, socio_id: int, activos: bool | None = None
) -> list[Prestamo]:
    query = select(Prestamo).where(Prestamo.socio_id == socio_id)
    if activos is True:
        query = query.where(Prestamo.fecha_devolucion.is_(None))
    return list(session.exec(query).all())


def guardar_prestamo_y_stock(
    session: Session, prestamo: Prestamo, libro: Libro | None = None
) -> Prestamo:
    session.add(prestamo)
    if libro is not None:
        session.add(libro)
    session.commit()
    session.refresh(prestamo)
    return prestamo