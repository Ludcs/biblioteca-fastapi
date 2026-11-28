from fastapi import APIRouter, HTTPException, status

from database import SessionDep
from models.prestamo import PrestamoRead
from models.socio import Socio, SocioCreate, SocioUpdate
from repositories.socio_repository import (
    eliminar_socio,
    guardar_socio,
    listar_socios,
    obtener_socio_por_email,
    obtener_socio_por_id,
)
from services.prestamos_service import obtener_prestamos_socio

router = APIRouter(prefix="/socios", tags=["Socios"])


@router.get("/", response_model=list[Socio])
def get_socios(session: SessionDep):
    return listar_socios(session)


@router.get("/{socio_id}", response_model=Socio)
def get_socio_by_id(socio_id: int, session: SessionDep):
    socio = obtener_socio_por_id(session, socio_id)
    if not socio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Socio no encontrado",
        )
    return socio


@router.post("/", response_model=Socio, status_code=status.HTTP_201_CREATED)
def create_socio(socio_data: SocioCreate, session: SessionDep):
    existente = obtener_socio_por_email(session, socio_data.email)
    if existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un socio registrado con ese email",
        )

    socio = Socio.model_validate(socio_data)
    return guardar_socio(session, socio)


@router.patch("/{socio_id}", response_model=Socio)
def update_socio(socio_id: int, socio_data: SocioUpdate, session: SessionDep):
    socio = obtener_socio_por_id(session, socio_id)
    if not socio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Socio no encontrado",
        )

    datos = socio_data.model_dump(exclude_unset=True)
    if "email" in datos and datos["email"] != socio.email:
        existente = obtener_socio_por_email(session, datos["email"])
        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un socio registrado con ese email",
            )

    socio.sqlmodel_update(datos)
    return guardar_socio(session, socio)


@router.delete("/{socio_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_socio(socio_id: int, session: SessionDep):
    socio = obtener_socio_por_id(session, socio_id)
    if not socio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Socio no encontrado",
        )

    eliminar_socio(session, socio)


@router.get("/{socio_id}/prestamos", response_model=list[PrestamoRead])
def get_prestamos_de_socio(
    socio_id: int, session: SessionDep, activos: bool | None = None
):
    return obtener_prestamos_socio(socio_id, session, activos=activos)