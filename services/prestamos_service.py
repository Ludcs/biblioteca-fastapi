from datetime import date, timedelta
from fastapi import HTTPException, status
from sqlmodel import Session

from models.prestamo import Prestamo, PrestamoCreate
from repositories.libro_repository import obtener_libro_por_id
from repositories.prestamo_repository import (
    contar_prestamos_activos_socio,
    guardar_prestamo_y_stock,
    listar_prestamos_socio,
    obtener_prestamo_por_id,
)
from repositories.socio_repository import obtener_socio_por_id

MONTO_MULTA_POR_DIA = 100.0
PLAZO_DIAS = 14


def crear_prestamo(data: PrestamoCreate, session: Session) -> Prestamo:
    socio = obtener_socio_por_id(session, data.socio_id)
    if not socio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Socio no encontrado",
        )

    libro = obtener_libro_por_id(session, data.libro_id)
    if not libro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Libro no encontrado",
        )

    if not socio.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El socio está inactivo y no puede pedir préstamos",
        )

    cantidad_activos = contar_prestamos_activos_socio(session, socio.id)
    if cantidad_activos >= 3:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El socio ya tiene el máximo de 3 préstamos activos",
        )

    if libro.stock <= 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No hay stock disponible para este libro",
        )

    hoy = date.today()
    prestamo = Prestamo(
        socio_id=socio.id,
        libro_id=libro.id,
        fecha_prestamo=hoy,
        fecha_vencimiento=hoy + timedelta(days=PLAZO_DIAS),
        fecha_devolucion=None,
        multa=0.0,
    )

    libro.stock -= 1
    return guardar_prestamo_y_stock(session, prestamo, libro=libro)


def devolver_prestamo(prestamo_id: int, session: Session) -> Prestamo:
    prestamo = obtener_prestamo_por_id(session, prestamo_id)
    if not prestamo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Préstamo no encontrado",
        )

    if prestamo.fecha_devolucion is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El préstamo ya fue devuelto",
        )

    hoy = date.today()
    prestamo.fecha_devolucion = hoy

    dias_atraso = (hoy - prestamo.fecha_vencimiento).days
    prestamo.multa = dias_atraso * MONTO_MULTA_POR_DIA if dias_atraso > 0 else 0.0

    libro = obtener_libro_por_id(session, prestamo.libro_id)
    if libro:
        libro.stock += 1

    return guardar_prestamo_y_stock(session, prestamo, libro=libro)


def obtener_prestamos_socio(
    socio_id: int, session: Session, activos: bool | None = None
) -> list[Prestamo]:
    socio = obtener_socio_por_id(session, socio_id)
    if not socio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Socio no encontrado",
        )

    return listar_prestamos_socio(session, socio_id, activos=activos)