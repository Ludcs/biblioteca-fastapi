from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from database import SessionDep
from models.autor import Autor, AutorCreate, AutorUpdate

router = APIRouter(prefix="/autores", tags=["Autores"])


@router.get("/", response_model=list[Autor])
def get_autores(session: SessionDep):
    return session.exec(select(Autor)).all()


@router.get("/{autor_id}", response_model=Autor)
def get_autor_by_id(autor_id: int, session: SessionDep):
    autor = session.get(Autor, autor_id)
    if not autor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Autor no encontrado",
        )
    return autor


@router.post("/", response_model=Autor, status_code=status.HTTP_201_CREATED)
def create_autor(autor_data: AutorCreate, session: SessionDep):
    autor = Autor.model_validate(autor_data)
    session.add(autor)
    session.commit()
    session.refresh(autor)
    return autor


@router.patch("/{autor_id}", response_model=Autor)
def update_autor(autor_id: int, autor_data: AutorUpdate, session: SessionDep):
    autor = session.get(Autor, autor_id)
    if not autor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Autor no encontrado",
        )

    datos = autor_data.model_dump(exclude_unset=True)
    autor.sqlmodel_update(datos)
    session.add(autor)
    session.commit()
    session.refresh(autor)
    return autor


@router.delete("/{autor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_autor(autor_id: int, session: SessionDep):
    autor = session.get(Autor, autor_id)
    if not autor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Autor no encontrado",
        )

    session.delete(autor)
    session.commit()