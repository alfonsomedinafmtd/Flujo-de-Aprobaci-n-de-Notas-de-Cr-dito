# Portal interno de Finanzas

Aplicación web para consultar la estructura organizacional de una VP de Finanzas y operar un flujo auditable de solicitudes de notas de crédito.

[![Abrir portal en GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/alfonsomedinafmtd/Flujo-de-Aprobaci-n-de-Notas-de-Cr-dito/tree/main)

El botón crea un entorno temporal en GitHub, instala el proyecto y abre el portal en el navegador sin requerir una instalación local.

## Alcance seleccionado

- Estructura organizacional con vistas relacionadas de colaboradores, departamentos, cargos, seniority y funciones.
- Creación, aprobación y rechazo de notas de crédito con segregación de funciones.
- Autenticación mediante sesión y autorización por rol y departamento en el backend.
- Historial inmutable de cada cambio de estado.
- Analítica administrativa por área, cargo, solicitante, período y estado.

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

Para ejecutar la revisión reproducible de seguridad —integridad y vulnerabilidades
de dependencias, análisis estático y patrones de secretos— se requiere conexión a
los registros oficiales:

```powershell
.\scripts\security-audit.ps1
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

### Apertura rápida

1. Selecciona [Abrir portal en GitHub Codespaces](https://codespaces.new/alfonsomedinafmtd/Flujo-de-Aprobaci-n-de-Notas-de-Cr-dito/tree/main).
2. Inicia sesión en GitHub si la plataforma lo solicita, confirma que la rama seleccionada sea `main` y pulsa **Create codespace**.
3. Espera a que finalice la creación del contenedor. La primera ejecución instala las dependencias y prepara los datos ficticios automáticamente.
4. Codespaces abrirá en el navegador el puerto `5173`, identificado como **Portal de Finanzas**.
5. Consulta `.devcontainer/.state/demo-credentials.txt` desde el explorador de VS Code para iniciar sesión con cualquiera de los roles generados.

Si el navegador no se abre automáticamente, entra en la pestaña **Ports**, localiza **Portal de Finanzas (5173)** y selecciona el icono **Open in Browser**.

### Actualizar un Codespace existente

Un Codespace conserva la versión del repositorio con la que fue creado. Si ya existe uno y muestra una interfaz anterior, ejecuta en su terminal:

```bash
git status --short
git switch main
git pull --ff-only origin main
bash .devcontainer/start.sh
```

El primer comando debe mostrar el árbol limpio antes de actualizar. Si existen cambios propios sin confirmar, deben conservarse mediante un commit o `git stash` antes del `pull`. Después de la actualización, recarga el navegador con `Ctrl+Shift+R` para descartar recursos almacenados en caché.

El repositorio incluye una configuración reproducible en `.devcontainer`. Al crear
un Codespace desde la rama `main` se instalan Python, Node.js y todas las
dependencias; luego se crea una base SQLite de demostración y se inician FastAPI
y Vite automáticamente.

Codespaces abre el portal reenviado por el puerto `5173`. Las credenciales
aleatorias se muestran en el registro de creación y permanecen solo dentro del
Codespace en `.devcontainer/.state/demo-credentials.txt`; este archivo está
ignorado por Git. La documentación técnica queda disponible en el puerto `8000`.
Los puertos son privados de manera predeterminada y no deben cambiarse a públicos.

El visualizador permanece disponible mientras el Codespace esté ejecutándose. Al detenerlo, su URL temporal deja de responder hasta volver a iniciarlo; esto no equivale a un despliegue permanente.

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

La solución incluye autenticación por sesión, protección CSRF, consultas de la estructura organizacional, migraciones, seed, el flujo completo de notas de crédito, analítica exclusiva para administradores y una interfaz React adaptada a los permisos de cada rol.

Las 29 pruebas automatizadas del backend cubren autenticación, aislamiento por departamento, segregación de funciones, transiciones de estado, auditoría, analítica administrativa, filtros, datos visibles, validaciones y configuración segura. El frontend superó typecheck, 3 pruebas Vitest y el build de producción. La auditoría final no encontró vulnerabilidades conocidas en Python o npm, hallazgos estáticos de Bandit ni patrones de secretos en archivos versionados.
