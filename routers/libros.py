from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from database import SessionDep
from models.libro import Libro, LibroCreate, LibroUpdate

router = APIRouter(prefix="/libros", tags=["Libros"])

@router.get("/", response_model=list[Libro])
def get_libros(session: SessionDep, disponibles: bool | None = None):
    query = select(Libro)
    if disponibles is True:
        query = query.where(Libro.stock > 0)
    return session.exec(query).all()


@router.get("/{libro_id}", response_model=Libro)
def get_libro_by_id(libro_id: int, session: SessionDep):
    libro = session.get(Libro, libro_id)
    if not libro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Libro no encontrado",
        )
    return libro


@router.post("/", response_model=Libro, status_code=status.HTTP_201_CREATED)
def create_libro(libro_data: LibroCreate, session: SessionDep):
    existe = session.exec(select(Libro).where(Libro.isbn == libro_data.isbn)).first()
    if existe:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un libro con ese ISBN",
        )

    libro = Libro.model_validate(libro_data)
    session.add(libro)
    session.commit()
    session.refresh(libro)
    return libro


@router.patch("/{libro_id}", response_model=Libro)
def update_libro(libro_id: int, libro_data: LibroUpdate, session: SessionDep):
    libro = session.get(Libro, libro_id)
    if not libro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Libro no encontrado",
        )

    datos = libro_data.model_dump(exclude_unset=True)

    if "isbn" in datos and datos["isbn"] != libro.isbn:
        existe = session.exec(select(Libro).where(Libro.isbn == datos["isbn"])).first()
        if existe:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un libro con ese ISBN",
            )

    libro.sqlmodel_update(datos)
    session.add(libro)
    session.commit()
    session.refresh(libro)
    return libro


@router.delete("/{libro_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_libro(libro_id: int, session: SessionDep):
    libro = session.get(Libro, libro_id)
    if not libro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Libro no encontrado",
        )

    session.delete(libro)
    session.commit()