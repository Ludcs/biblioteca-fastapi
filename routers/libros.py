from fastapi import APIRouter, HTTPException, status

from database import SessionDep
from models.libro import Libro, LibroCreate, LibroUpdate
from repositories.autor_repository import obtener_autor_por_id
from repositories.libro_repository import (
    eliminar_libro,
    guardar_libro,
    listar_libros,
    obtener_libro_por_id,
    obtener_libro_por_isbn,
)

router = APIRouter(prefix="/libros", tags=["Libros"])


@router.get("/", response_model=list[Libro])
def get_libros(session: SessionDep, disponibles: bool | None = None):
    return listar_libros(session, disponibles=disponibles)


@router.get("/{libro_id}", response_model=Libro)
def get_libro_by_id(libro_id: int, session: SessionDep):
    libro = obtener_libro_por_id(session, libro_id)
    if not libro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Libro no encontrado",
        )
    return libro


@router.post("/", response_model=Libro, status_code=status.HTTP_201_CREATED)
def create_libro(libro_data: LibroCreate, session: SessionDep):
    existente = obtener_libro_por_isbn(session, libro_data.isbn)
    if existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un libro registrado con ese ISBN",
        )

    libro = Libro.model_validate(libro_data)
    return guardar_libro(session, libro)


@router.patch("/{libro_id}", response_model=Libro)
def update_libro(libro_id: int, libro_data: LibroUpdate, session: SessionDep):
    libro = obtener_libro_por_id(session, libro_id)
    if not libro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Libro no encontrado",
        )

    datos = libro_data.model_dump(exclude_unset=True)
    if "isbn" in datos and datos["isbn"] != libro.isbn:
        existente = obtener_libro_por_isbn(session, datos["isbn"])
        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un libro registrado con ese ISBN",
            )

    libro.sqlmodel_update(datos)
    return guardar_libro(session, libro)


@router.delete("/{libro_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_libro(libro_id: int, session: SessionDep):
    libro = obtener_libro_por_id(session, libro_id)
    if not libro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Libro no encontrado",
        )

    eliminar_libro(session, libro)


@router.post(
    "/{libro_id}/autores/{autor_id}",
    response_model=Libro,
    status_code=status.HTTP_201_CREATED,
)
def asociar_autor_a_libro(libro_id: int, autor_id: int, session: SessionDep):
    libro = obtener_libro_por_id(session, libro_id)
    if not libro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Libro no encontrado",
        )

    autor = obtener_autor_por_id(session, autor_id)
    if not autor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Autor no encontrado",
        )

    if autor not in libro.autores:
        libro.autores.append(autor)
        guardar_libro(session, libro)

    return libro