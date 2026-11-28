from fastapi import APIRouter, HTTPException, status

from database import SessionDep
from models.autor import Autor, AutorCreate, AutorUpdate
from repositories.autor_repository import (
    eliminar_autor,
    guardar_autor,
    listar_autores,
    obtener_autor_por_id,
)

router = APIRouter(prefix="/autores", tags=["Autores"])


@router.get("/", response_model=list[Autor])
def get_autores(session: SessionDep):
    return listar_autores(session)


@router.get("/{autor_id}", response_model=Autor)
def get_autor_by_id(autor_id: int, session: SessionDep):
    autor = obtener_autor_por_id(session, autor_id)
    if not autor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Autor no encontrado",
        )
    return autor


@router.post("/", response_model=Autor, status_code=status.HTTP_201_CREATED)
def create_autor(autor_data: AutorCreate, session: SessionDep):
    autor = Autor.model_validate(autor_data)
    return guardar_autor(session, autor)


@router.patch("/{autor_id}", response_model=Autor)
def update_autor(autor_id: int, autor_data: AutorUpdate, session: SessionDep):
    autor = obtener_autor_por_id(session, autor_id)
    if not autor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Autor no encontrado",
        )

    datos = autor_data.model_dump(exclude_unset=True)
    autor.sqlmodel_update(datos)
    return guardar_autor(session, autor)


@router.delete("/{autor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_autor(autor_id: int, session: SessionDep):
    autor = obtener_autor_por_id(session, autor_id)
    if not autor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Autor no encontrado",
        )

    eliminar_autor(session, autor)