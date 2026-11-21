from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import create_db_and_tables
from routers.autores import router as autores_router
from routers.socios import router as socios_router
from routers.libros import router as libros_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="API Biblioteca - Programación 4", lifespan=lifespan)
app.include_router(autores_router)
app.include_router(socios_router)
app.include_router(libros_router)

@app.get("/")
def root():
    return {"status": "ok"}