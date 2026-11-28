from sqlmodel import Session, select

from models.libro import Libro


def listar_libros(
    session: Session, disponibles: bool | None = None
) -> list[Libro]:
    query = select(Libro)
    if disponibles is True:
        query = query.where(Libro.stock > 0)
    return list(session.exec(query).all())


def obtener_libro_por_id(session: Session, libro_id: int) -> Libro | None:
    return session.get(Libro, libro_id)


def obtener_libro_por_isbn(session: Session, isbn: str) -> Libro | None:
    statement = select(Libro).where(Libro.isbn == isbn)
    return session.exec(statement).first()


def guardar_libro(session: Session, libro: Libro) -> Libro:
    session.add(libro)
    session.commit()
    session.refresh(libro)
    return libro


def eliminar_libro(session: Session, libro: Libro) -> None:
    session.delete(libro)
    session.commit()