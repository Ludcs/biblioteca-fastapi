from datetime import date, timedelta
from fastapi.testclient import TestClient
from sqlmodel import Session

from models.prestamo import Prestamo


def _crear_socio(client: TestClient, email: str = "socio@test.com", activo: bool = True) -> dict:
    resp = client.post(
        "/socios/",
        json={"nombre": "Socio Test", "email": email, "activo": activo},
    )
    assert resp.status_code == 201
    return resp.json()

def _crear_libro(client: TestClient, isbn: str = "ISBN-TEST-1", stock: int = 5) -> dict:
    resp = client.post(
        "/libros/",
        json={"titulo": "Libro Test", "isbn": isbn, "stock": stock, "anio": 2020},
    )
    assert resp.status_code == 201
    return resp.json()

def test_crear_prestamo_descuenta_stock_y_calcula_vencimiento(client: TestClient):
    socio = _crear_socio(client, email="uno@test.com")
    libro = _crear_libro(client, isbn="ISBN-100", stock=3)

    resp = client.post(
        "/prestamos/",
        json={"socio_id": socio["id"], "libro_id": libro["id"]},
    )
    assert resp.status_code == 201
    data = resp.json()

    fecha_prestamo = date.fromisoformat(data["fecha_prestamo"])
    fecha_vencimiento = date.fromisoformat(data["fecha_vencimiento"])
    assert fecha_vencimiento == fecha_prestamo + timedelta(days=14)
    assert data["fecha_devolucion"] is None
    assert data["multa"] == 0.0

    libro_actualizado = client.get(f"/libros/{libro['id']}").json()
    assert libro_actualizado["stock"] == 2

def test_socio_inactivo_no_puede_pedir_prestamo_403(client: TestClient):
    socio = _crear_socio(client, email="inactivo@test.com", activo=False)
    libro = _crear_libro(client, isbn="ISBN-101", stock=2)

    resp = client.post(
        "/prestamos/",
        json={"socio_id": socio["id"], "libro_id": libro["id"]},
    )
    assert resp.status_code == 403

def test_libro_sin_stock_devuelve_409(client: TestClient):
    socio = _crear_socio(client, email="sinstock@test.com")
    libro = _crear_libro(client, isbn="ISBN-102", stock=0)

    resp = client.post(
        "/prestamos/",
        json={"socio_id": socio["id"], "libro_id": libro["id"]},
    )
    assert resp.status_code == 409

def test_maximo_tres_prestamos_activos_devuelve_409(client: TestClient):
    socio = _crear_socio(client, email="lector@test.com")

    for i in range(3):
        libro = _crear_libro(client, isbn=f"ISBN-MAX-{i}", stock=2)
        resp = client.post(
            "/prestamos/",
            json={"socio_id": socio["id"], "libro_id": libro["id"]},
        )
        assert resp.status_code == 201

    libro_extra = _crear_libro(client, isbn="ISBN-MAX-4", stock=2)
    cuarto = client.post(
        "/prestamos/",
        json={"socio_id": socio["id"], "libro_id": libro_extra["id"]},
    )
    assert cuarto.status_code == 409

def test_devolver_prestamo_repone_stock_y_bloquea_doble_devolucion(client: TestClient):
    socio = _crear_socio(client, email="devuelve@test.com")
    libro = _crear_libro(client, isbn="ISBN-DEV-1", stock=1)

    prestamo = client.post(
        "/prestamos/",
        json={"socio_id": socio["id"], "libro_id": libro["id"]},
    ).json()
    assert client.get(f"/libros/{libro['id']}").json()["stock"] == 0

    devolucion = client.post(f"/prestamos/{prestamo['id']}/devolucion")
    assert devolucion.status_code == 200
    assert devolucion.json()["fecha_devolucion"] is not None
    assert devolucion.json()["multa"] == 0.0

    assert client.get(f"/libros/{libro['id']}").json()["stock"] == 1

    repetida = client.post(f"/prestamos/{prestamo['id']}/devolucion")
    assert repetida.status_code == 409

def test_listar_prestamos_activos_de_socio(client: TestClient):
    socio = _crear_socio(client, email="activos@test.com")
    libro_1 = _crear_libro(client, isbn="ISBN-ACT-1", stock=2)
    libro_2 = _crear_libro(client, isbn="ISBN-ACT-2", stock=2)

    p1 = client.post(
        "/prestamos/",
        json={"socio_id": socio["id"], "libro_id": libro_1["id"]},
    ).json()
    client.post(
        "/prestamos/",
        json={"socio_id": socio["id"], "libro_id": libro_2["id"]},
    )

    client.post(f"/prestamos/{p1['id']}/devolucion")

    activos = client.get(f"/socios/{socio['id']}/prestamos?activos=true")
    assert activos.status_code == 200
    assert len(activos.json()) == 1
    assert activos.json()[0]["libro_id"] == libro_2["id"]

def test_devolucion_con_atraso_calcula_multa(client: TestClient, session: Session):
    socio = _crear_socio(client, email="moroso@test.com")
    libro = _crear_libro(client, isbn="ISBN-MULTA-1", stock=2)

    prestamo_data = client.post(
        "/prestamos/",
        json={"socio_id": socio["id"], "libro_id": libro["id"]},
    ).json()

    prestamo_db = session.get(Prestamo, prestamo_data["id"])
    assert prestamo_db is not None
    prestamo_db.fecha_vencimiento = date.today() - timedelta(days=5)
    session.add(prestamo_db)
    session.commit()

    devolucion = client.post(f"/prestamos/{prestamo_data['id']}/devolucion")
    assert devolucion.status_code == 200
    assert devolucion.json()["multa"] == 500.0