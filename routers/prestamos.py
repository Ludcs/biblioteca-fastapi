from fastapi import APIRouter, status

from database import SessionDep
from models.prestamo import PrestamoCreate, PrestamoRead
from services.prestamos_service import crear_prestamo, devolver_prestamo

router = APIRouter(prefix="/prestamos", tags=["Préstamos"])


@router.post("/", response_model=PrestamoRead, status_code=status.HTTP_201_CREATED)
def registrar_prestamo(data: PrestamoCreate, session: SessionDep):
    return crear_prestamo(data, session)


@router.post("/{prestamo_id}/devolucion", response_model=PrestamoRead)
def registrar_devolucion(prestamo_id: int, session: SessionDep):
    return devolver_prestamo(prestamo_id, session)