from datetime import date
from typing import TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from models.libro import Libro
    from models.socio import Socio


class Prestamo(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    socio_id: int = Field(foreign_key="socio.id")
    libro_id: int = Field(foreign_key="libro.id")
    fecha_prestamo: date
    fecha_vencimiento: date
    fecha_devolucion: date | None = Field(default=None)
    multa: float = Field(default=0.0, ge=0)

    socio: "Socio" = Relationship(back_populates="prestamos")
    libro: "Libro" = Relationship(back_populates="prestamos")