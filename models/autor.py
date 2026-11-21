from typing import TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel

from models.links import LibroAutor

if TYPE_CHECKING:
    from models.libro import Libro


class Autor(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(min_length=1)
    nacionalidad: str = Field(min_length=1)

    libros: list["Libro"] = Relationship(back_populates="autores", link_model=LibroAutor)