from fastapi.testclient import TestClient


def test_crear_y_listar_autores(client: TestClient):
    response = client.post(
        "/autores/",
        json={"nombre": "Jorge Luis Borges", "nacionalidad": "Argentina"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "Jorge Luis Borges"
    assert data["nacionalidad"] == "Argentina"
    assert "id" in data

    lista = client.get("/autores/")
    assert lista.status_code == 200
    assert len(lista.json()) == 1

def test_obtener_autor_por_id(client: TestClient):
    creado = client.post(
        "/autores/",
        json={"nombre": "Julio Cortázar", "nacionalidad": "Argentina"},
    ).json()

    response = client.get(f"/autores/{creado['id']}")
    assert response.status_code == 200
    assert response.json()["nombre"] == "Julio Cortázar"

def test_obtener_autor_inexistente_devuelve_404(client: TestClient):
    response = client.get("/autores/999")
    assert response.status_code == 404

def test_actualizar_autor(client: TestClient):
    creado = client.post(
        "/autores/",
        json={"nombre": "Gabriel Garcia Marquez", "nacionalidad": "Colombia"},
    ).json()

    response = client.patch(
        f"/autores/{creado['id']}",
        json={"nombre": "Gabriel García Márquez"},
    )
    assert response.status_code == 200
    assert response.json()["nombre"] == "Gabriel García Márquez"
    assert response.json()["nacionalidad"] == "Colombia"

def test_actualizar_autor_inexistente_devuelve_404(client: TestClient):
    response = client.patch("/autores/999", json={"nombre": "No Existe"})
    assert response.status_code == 404

def test_eliminar_autor(client: TestClient):
    creado = client.post(
        "/autores/",
        json={"nombre": "Horacio Quiroga", "nacionalidad": "Uruguay"},
    ).json()

    delete_resp = client.delete(f"/autores/{creado['id']}")
    assert delete_resp.status_code == 204

    get_resp = client.get(f"/autores/{creado['id']}")
    assert get_resp.status_code == 404


def test_eliminar_autor_inexistente_devuelve_404(client: TestClient):
    response = client.delete("/autores/999")
    assert response.status_code == 404