from sqlmodel import Session, select

from models.autor import Autor


def listar_autores(session: Session) -> list[Autor]:
    return list(session.exec(select(Autor)).all())


def obtener_autor_por_id(session: Session, autor_id: int) -> Autor | None:
    return session.get(Autor, autor_id)


def guardar_autor(session: Session, autor: Autor) -> Autor:
    session.add(autor)
    session.commit()
    session.refresh(autor)
    return autor


def eliminar_autor(session: Session, autor: Autor) -> None:
    session.delete(autor)
    session.commit()