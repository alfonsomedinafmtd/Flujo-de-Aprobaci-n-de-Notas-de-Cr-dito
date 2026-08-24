# Portal interno de Finanzas

Aplicación web para consultar la estructura organizacional de una VP de Finanzas y operar un flujo auditable de solicitudes de notas de crédito.

## Alcance seleccionado

- Directorio de departamentos y colaboradores ficticios.
- Catálogo de cargos, seniority y funciones.
- Creación, aprobación y rechazo de notas de crédito con segregación de funciones.
- Autenticación mediante sesión y autorización por rol y departamento en el backend.
- Historial inmutable de cada cambio de estado.

## Stack decidido

- Backend: Python, FastAPI y SQLAlchemy.
- Base de datos inicial: SQLite, aceptada por el enunciado y portable a PostgreSQL.
- Frontend: React con TypeScript y Vite.
- Pruebas: pytest para reglas de negocio y autorización; Vitest para componentes críticos.

Las decisiones y sus motivos se mantienen en [docs/DECISIONS.md](docs/DECISIONS.md).

## Ejecutar el backend en Windows

Requisitos: Python 3.12 o superior.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements-dev.txt
Copy-Item .env.example backend\.env
Set-Location backend
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

El seed crea 4 departamentos, 33 colaboradores ficticios y adapta las 25 notas de crédito proporcionadas. Las contraseñas demo se generan aleatoriamente y se muestran una sola vez al crear una base vacía; no se guardan en el repositorio.

La API queda disponible en `http://localhost:8000` y su documentación OpenAPI en `http://localhost:8000/docs`.

Para ejecutar las pruebas:

```powershell
Set-Location backend
python -m pytest
```

## Seguridad prevista

- El rol y el departamento se obtienen exclusivamente de la sesión autenticada.
- Las contraseñas se almacenan con un algoritmo de derivación seguro, nunca en texto plano.
- La sesión se transporta en una cookie `HttpOnly` y los cambios de estado requieren protección CSRF.
- Los secretos y la configuración local permanecen fuera del repositorio.
- Las solicitudes y sus eventos de auditoría no admiten eliminación física.

## Estado

El backend ya incluye autenticación por sesión, protección CSRF, organización, migraciones, seed y el flujo completo de notas de crédito. El frontend React continúa en construcción.
