from fastapi.testclient import TestClient

def test_crear_y_listar_socios(client: TestClient):
    response = client.post(
        "/socios/",
        json={
            "nombre": "Ana Pérez",
            "email": "ana@example.com",
            "activo": True,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "Ana Pérez"
    assert data["email"] == "ana@example.com"
    assert data["activo"] is True
    assert "id" in data

    lista = client.get("/socios/")
    assert lista.status_code == 200
    assert len(lista.json()) == 1

def test_crear_socio_email_duplicado_devuelve_409(client: TestClient):
    payload = {
        "nombre": "Ana Pérez",
        "email": "ana@example.com",
        "activo": True,
    }
    primero = client.post("/socios/", json=payload)
    assert primero.status_code == 201

    duplicado = client.post(
        "/socios/",
        json={
            "nombre": "Otra Ana",
            "email": "ana@example.com",
            "activo": True,
        },
    )
    assert duplicado.status_code == 409

def test_obtener_socio_por_id_y_404(client: TestClient):
    creado = client.post(
        "/socios/",
        json={"nombre": "Luis Gómez", "email": "luis@example.com"},
    ).json()

    ok = client.get(f"/socios/{creado['id']}")
    assert ok.status_code == 200
    assert ok.json()["email"] == "luis@example.com"

    no_existe = client.get("/socios/999")
    assert no_existe.status_code == 404

def test_actualizar_socio_y_validar_email_duplicado(client: TestClient):
    socio_1 = client.post(
        "/socios/",
        json={"nombre": "Socio Uno", "email": "uno@example.com"},
    ).json()
    socio_2 = client.post(
        "/socios/",
        json={"nombre": "Socio Dos", "email": "dos@example.com"},
    ).json()

    update_ok = client.patch(
        f"/socios/{socio_1['id']}",
        json={"nombre": "Socio Uno Editado", "activo": False},
    )
    assert update_ok.status_code == 200
    assert update_ok.json()["nombre"] == "Socio Uno Editado"
    assert update_ok.json()["activo"] is False

    conflicto = client.patch(
        f"/socios/{socio_2['id']}",
        json={"email": "uno@example.com"},
    )
    assert conflicto.status_code == 409

    no_existe = client.patch("/socios/999", json={"nombre": "Nadie"})
    assert no_existe.status_code == 404

def test_eliminar_socio_y_404(client: TestClient):
    creado = client.post(
        "/socios/",
        json={"nombre": "Carlos Ruiz", "email": "carlos@example.com"},
    ).json()

    borrado = client.delete(f"/socios/{creado['id']}")
    assert borrado.status_code == 204

    despues = client.get(f"/socios/{creado['id']}")
    assert despues.status_code == 404

    no_existe = client.delete("/socios/999")
    assert no_existe.status_code == 404