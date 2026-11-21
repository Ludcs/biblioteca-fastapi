from typing import TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from models.prestamo import Prestamo
class Socio(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(min_length=1)
    email: str = Field(unique=True, index=True, min_length=1)
    activo: bool = Field(default=True)

    prestamos: list["Prestamo"] = Relationship(back_populates="socio")
class SocioCreate(SQLModel):
    nombre: str = Field(min_length=1)
    email: str = Field(min_length=1)
    activo: bool = True
class SocioUpdate(SQLModel):
    nombre: str | None = Field(default=None, min_length=1)
    email: str | None = Field(default=None, min_length=1)
    activo: bool | None = None