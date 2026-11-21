from typing import TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel

from models.links import LibroAutor

if TYPE_CHECKING:
    from models.autor import Autor
    from models.prestamo import Prestamo


class Libro(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    titulo: str = Field(min_length=1)
    isbn: str = Field(unique=True, index=True, min_length=1)
    stock: int = Field(default=0, ge=0)
    anio: int

    autores: list["Autor"] = Relationship(back_populates="libros", link_model=LibroAutor)
    prestamos: list["Prestamo"] = Relationship(back_populates="libro")
class LibroCreate(SQLModel):
    titulo: str = Field(min_length=1)
    isbn: str = Field(min_length=1)
    stock: int = Field(default=0, ge=0)
    anio: int
class LibroUpdate(SQLModel):
    titulo: str | None = Field(default=None, min_length=1)
    isbn: str | None = Field(default=None, min_length=1)
    stock: int | None = Field(default=None, ge=0)
    anio: int | None = None