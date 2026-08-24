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

Las decisiones y sus motivos se mantienen en [docs/DECISIONS.md](docs/DECISIONS.md). La cobertura del enunciado puede revisarse en [docs/REQUIREMENTS_TRACEABILITY.md](docs/REQUIREMENTS_TRACEABILITY.md) y el recorrido recomendado para presentar la solución está en [docs/DEMO_GUIDE.md](docs/DEMO_GUIDE.md).

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

También se puede ejecutar toda la verificación disponible del backend desde la raíz:

```powershell
.\scripts\verify.ps1 -BackendOnly
```

## Ejecutar el frontend

Requisitos: Node.js 24 LTS o una versión compatible con Vite 8.

```powershell
Set-Location frontend
Copy-Item .env.example .env
npm install
npm run dev
```

La interfaz queda disponible en `http://localhost:5173`. La cookie de sesión se envía con `credentials: include`; el token CSRF se conserva únicamente en memoria y se rota al restaurar la sesión.

Para validar tipos, pruebas y build de producción:

```powershell
npm run typecheck
npm test
npm run build
```

Cuando las dependencias estén instaladas, el verificador completo ejecuta backend, tipos, pruebas y build:

```powershell
Set-Location ..
.\scripts\verify.ps1
```

## Seguridad implementada

- El rol y el departamento se obtienen exclusivamente de la sesión autenticada.
- Las contraseñas se almacenan con un algoritmo de derivación seguro, nunca en texto plano.
- La sesión se transporta en una cookie `HttpOnly` y los cambios de estado requieren protección CSRF.
- Los secretos y la configuración local permanecen fuera del repositorio.
- Las solicitudes y sus eventos de auditoría no admiten eliminación física.

## Estado de la entrega

La solución incluye autenticación por sesión, protección CSRF, consultas de la estructura organizacional, migraciones, seed, el flujo completo de notas de crédito y una interfaz React adaptada a los permisos de cada rol.

Las pruebas automatizadas del backend cubren autenticación, aislamiento por departamento, segregación de funciones, transiciones de estado, auditoría y configuración segura. El frontend incluye una prueba de las reglas de visibilidad por rol y scripts para validar tipos, pruebas y build.
