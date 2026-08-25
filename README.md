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

## Documentación

- [Decisiones técnicas](docs/DECISIONS.md)
- [Modelo relacional](docs/ERD.md)
- [Matriz de permisos](docs/PERMISSIONS.md)
- [Trazabilidad de requisitos](docs/REQUIREMENTS_TRACEABILITY.md)
- [Guía práctica de la API](docs/API_GUIDE.md)
- [Guía de demostración](docs/DEMO_GUIDE.md)
- [Guía de defensa técnica](docs/TECHNICAL_DEFENSE.md)
- [Registro de uso de IA](docs/AI_USAGE.md)
- [Checklist de entrega](docs/DELIVERY_CHECKLIST.md)

El registro de IA incluye los prompts principales, las sugerencias aceptadas, modificadas y rechazadas con sus motivos, tres errores concretos detectados y su corrección, y un mapa de archivos para la posible explicación o modificación en vivo.

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

Para revisar el estado de entrega sin modificar el repositorio:

```powershell
.\scripts\delivery-audit.ps1
```

## Ejecutar el frontend

Requisitos: Node.js 24 LTS o una versión compatible con Vite 8.

```powershell
Set-Location frontend
Copy-Item .env.example .env
npm ci
npm run dev
```

La interfaz queda disponible en `http://localhost:5173`. La cookie de sesión se envía con `credentials: include`; el token CSRF se conserva únicamente en memoria y se rota al restaurar la sesión.

## Ejecutar en GitHub Codespaces

[Crear y abrir el Codespace](https://codespaces.new/alfonsomedinafmtd/Flujo-de-Aprobaci-n-de-Notas-de-Cr-dito?quickstart=1)

El repositorio incluye una configuración reproducible en `.devcontainer`. Al crear
un Codespace desde la rama `main` se instalan Python, Node.js y todas las
dependencias; luego se crea una base SQLite de demostración y se inician FastAPI
y Vite automáticamente.

Codespaces abre el portal reenviado por el puerto `5173`. Las credenciales
aleatorias se muestran en el registro de creación y permanecen solo dentro del
Codespace en `.devcontainer/.state/demo-credentials.txt`; este archivo está
ignorado por Git. La documentación técnica queda disponible en el puerto `8000`.
Los puertos son privados de manera predeterminada y no deben cambiarse a públicos.

Si el contenedor ya está creado y se necesita arrancar nuevamente los servicios:

```bash
bash .devcontainer/start.sh
```

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

Con la API iniciada, el flujo completo también puede demostrarse desde PowerShell sin guardar credenciales:

```powershell
.\scripts\demo-api.ps1 -Decision approve -Comment "Soporte validado"
```

## Seguridad implementada

- El rol y el departamento se obtienen exclusivamente de la sesión autenticada.
- Las contraseñas se almacenan con un algoritmo de derivación seguro, nunca en texto plano.
- La sesión se transporta en una cookie `HttpOnly` y los cambios de estado requieren protección CSRF.
- Los secretos y la configuración local permanecen fuera del repositorio.
- Las solicitudes y sus eventos de auditoría no admiten eliminación física.

## Estado de la entrega

La solución incluye autenticación por sesión, protección CSRF, consultas de la estructura organizacional, migraciones, seed, el flujo completo de notas de crédito y una interfaz React adaptada a los permisos de cada rol.

Las 27 pruebas automatizadas del backend cubren autenticación, aislamiento por departamento, segregación de funciones, transiciones de estado, auditoría, datos visibles de solicitantes y colaboradores, validaciones y configuración segura. El frontend superó typecheck, 2 pruebas Vitest y el build de producción; la auditoría npm reportó cero vulnerabilidades.
