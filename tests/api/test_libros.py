from fastapi.testclient import TestClient

def test_crear_y_listar_libros(client: TestClient):
    response = client.post(
        "/libros/",
        json={
            "titulo": "El Aleph",
            "isbn": "978-950-04-0001-1",
            "stock": 4,
            "anio": 1949,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["titulo"] == "El Aleph"
    assert data["isbn"] == "978-950-04-0001-1"
    assert data["stock"] == 4
    assert data["anio"] == 1949
    # assert data["autores"] == []
    assert "id" in data

    lista = client.get("/libros/")
    assert lista.status_code == 200
    assert len(lista.json()) == 1

def test_crear_libro_isbn_duplicado_devuelve_409(client: TestClient):
    payload = {
        "titulo": "Ficciones",
        "isbn": "978-950-04-0002-8",
        "stock": 2,
        "anio": 1944,
    }
    primero = client.post("/libros/", json=payload)
    assert primero.status_code == 201

    duplicado = client.post(
        "/libros/",
        json={
            "titulo": "Ficciones (reedición)",
            "isbn": "978-950-04-0002-8",
            "stock": 5,
            "anio": 1956,
        },
    )
    assert duplicado.status_code == 409

def test_filtrar_libros_disponibles(client: TestClient):
    client.post(
        "/libros/",
        json={
            "titulo": "Libro Sin Stock",
            "isbn": "ISBN-SIN-STOCK",
            "stock": 0,
            "anio": 2000,
        },
    )
    client.post(
        "/libros/",
        json={
            "titulo": "Libro Disponible",
            "isbn": "ISBN-DISPONIBLE",
            "stock": 3,
            "anio": 2010,
        },
    )

    disponibles = client.get("/libros/?disponibles=true")
    assert disponibles.status_code == 200
    items = disponibles.json()
    assert len(items) == 1
    assert items[0]["titulo"] == "Libro Disponible"
    assert items[0]["stock"] > 0

def test_obtener_libro_por_id_y_404(client: TestClient):
    creado = client.post(
        "/libros/",
        json={
            "titulo": "Rayuela",
            "isbn": "ISBN-RAYUELA",
            "stock": 2,
            "anio": 1963,
        },
    ).json()

    ok = client.get(f"/libros/{creado['id']}")
    assert ok.status_code == 200
    assert ok.json()["titulo"] == "Rayuela"

    no_existe = client.get("/libros/999")
    assert no_existe.status_code == 404

def test_actualizar_libro_y_validar_isbn_duplicado(client: TestClient):
    libro_1 = client.post(
        "/libros/",
        json={
            "titulo": "Libro Uno",
            "isbn": "ISBN-1",
            "stock": 2,
            "anio": 2001,
        },
    ).json()
    libro_2 = client.post(
        "/libros/",
        json={
            "titulo": "Libro Dos",
            "isbn": "ISBN-2",
            "stock": 1,
            "anio": 2002,
        },
    ).json()

    actualizado = client.patch(
        f"/libros/{libro_1['id']}",
        json={"titulo": "Libro Uno Actualizado", "stock": 6},
    )
    assert actualizado.status_code == 200
    assert actualizado.json()["titulo"] == "Libro Uno Actualizado"
    assert actualizado.json()["stock"] == 6

    conflicto = client.patch(
        f"/libros/{libro_2['id']}",
        json={"isbn": "ISBN-1"},
    )
    assert conflicto.status_code == 409

    no_existe = client.patch("/libros/999", json={"titulo": "Nada"})
    assert no_existe.status_code == 404

def test_eliminar_libro_y_404(client: TestClient):
    creado = client.post(
        "/libros/",
        json={
            "titulo": "Para Borrar",
            "isbn": "ISBN-BORRAR",
            "stock": 1,
            "anio": 1999,
        },
    ).json()

    borrado = client.delete(f"/libros/{creado['id']}")
    assert borrado.status_code == 204

    despues = client.get(f"/libros/{creado['id']}")
    assert despues.status_code == 404

    no_existe = client.delete("/libros/999")
    assert no_existe.status_code == 404

def test_asociar_autor_a_libro_y_404(client: TestClient):
    autor = client.post(
        "/autores/",
        json={"nombre": "Silvina Ocampo", "nacionalidad": "Argentina"},
    ).json()
    libro = client.post(
        "/libros/",
        json={
            "titulo": "La furia",
            "isbn": "ISBN-FURIA",
            "stock": 3,
            "anio": 1959,
        },
    ).json()

    asociacion = client.post(f"/libros/{libro['id']}/autores/{autor['id']}")
    assert asociacion.status_code == 201
    data = asociacion.json()
    assert len(data["autores"]) == 1
    assert data["autores"][0]["nombre"] == "Silvina Ocampo"

    repetida = client.post(f"/libros/{libro['id']}/autores/{autor['id']}")
    assert repetida.status_code == 201
    assert len(repetida.json()["autores"]) == 1

    assert client.post(f"/libros/999/autores/{autor['id']}").status_code == 404
    assert client.post(f"/libros/{libro['id']}/autores/999").status_code == 404