# API Biblioteca

API REST desarrollada con **FastAPI**, **SQLModel** y **SQLite** para la gestión de autores, libros, socios y préstamos.

## Requisitos previos

- Python 3.15+
- Entorno virtual (`venv`)

## Instalación y ejecución

1. Crear y activar el entorno virtual:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Instalar dependencias
    ```bash
    pip install -r requirements.txt
    ```

3. Levantar el servidor de desarrollo
    ```bash
    fastapi dev main.py
    ```

**La documentación interactiva queda disponible en http://127.0.0.1:8000/docs.**

# Tests y cobertura
Ejecutar el siguiente comando y ver el reporte de cobertura
    ```bash
    pytest --cov=. --cov-report=term-missing
    ```
