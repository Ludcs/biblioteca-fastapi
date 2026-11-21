from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from database import SessionDep
from models.socio import Socio, SocioCreate, SocioUpdate
from models.prestamo import PrestamoRead
from services.prestamos_service import obtener_prestamos_socio

router = APIRouter(prefix="/socios", tags=["Socios"])


@router.get("/", response_model=list[Socio])
def get_socios(session: SessionDep):
    return session.exec(select(Socio)).all()


@router.get("/{socio_id}", response_model=Socio)
def get_socio_by_id(socio_id: int, session: SessionDep):
    socio = session.get(Socio, socio_id)
    if not socio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Socio no encontrado",
        )
    return socio


@router.post("/", response_model=Socio, status_code=status.HTTP_201_CREATED)
def create_socio(socio_data: SocioCreate, session: SessionDep):
    existe = session.exec(select(Socio).where(Socio.email == socio_data.email)).first()
    if existe:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un socio con ese email",
        )

    socio = Socio.model_validate(socio_data)
    session.add(socio)
    session.commit()
    session.refresh(socio)
    return socio


@router.patch("/{socio_id}", response_model=Socio)
def update_socio(socio_id: int, socio_data: SocioUpdate, session: SessionDep):
    socio = session.get(Socio, socio_id)
    if not socio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Socio no encontrado",
        )

    datos = socio_data.model_dump(exclude_unset=True)

    if "email" in datos and datos["email"] != socio.email:
        existe = session.exec(select(Socio).where(Socio.email == datos["email"])).first()
        if existe:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un socio con ese email",
            )

    socio.sqlmodel_update(datos)
    session.add(socio)
    session.commit()
    session.refresh(socio)
    return socio


@router.delete("/{socio_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_socio(socio_id: int, session: SessionDep):
    socio = session.get(Socio, socio_id)
    if not socio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Socio no encontrado",
        )

    session.delete(socio)
    session.commit()

@router.get("/{socio_id}/prestamos", response_model=list[PrestamoRead])
def get_prestamos_de_socio(
    socio_id: int, session: SessionDep, activos: bool | None = None
):
    return obtener_prestamos_socio(socio_id, session, activos=activos)