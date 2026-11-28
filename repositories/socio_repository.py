from sqlmodel import Session, select

from models.socio import Socio


def listar_socios(session: Session) -> list[Socio]:
    return list(session.exec(select(Socio)).all())


def obtener_socio_por_id(session: Session, socio_id: int) -> Socio | None:
    return session.get(Socio, socio_id)


def obtener_socio_por_email(session: Session, email: str) -> Socio | None:
    statement = select(Socio).where(Socio.email == email)
    return session.exec(statement).first()


def guardar_socio(session: Session, socio: Socio) -> Socio:
    session.add(socio)
    session.commit()
    session.refresh(socio)
    return socio


def eliminar_socio(session: Session, socio: Socio) -> None:
    session.delete(socio)
    session.commit()