# Trazabilidad de requisitos

Esta matriz relaciona los requisitos del enunciado principal con la implementación entregada y su evidencia verificable.

| Requisito | Implementación | Evidencia |
|---|---|---|
| Al menos cuatro departamentos | Cuentas por Cobrar, Cuentas por Pagar, Planificación Financiera y Tesorería | `backend/app/seed.py` y módulo Organización |
| Entre 8 y 12 colaboradores ficticios por departamento | Ocho colaboradores base en cada departamento; el administrador pertenece adicionalmente a Planificación | Mensaje final del seed: 4 departamentos y 33 colaboradores |
| Detalle de cada colaborador | Nombre, país, fecha de ingreso, correo ficticio, estado, cargo, departamento, usuario y rol del portal | Endpoints `/organization/profile` y `/organization/employees`, y vista Organización según rol |
| Cargos, seniority y funciones normalizados | `positions`, `business_functions` y relación muchos-a-muchos `position_functions` | Migración inicial, `docs/ERD.md` y módulo Cargos y funciones |
| Roles Administrador, Jefe y Colaborador | `UserRole` y autorización derivada exclusivamente de la sesión | `docs/PERMISSIONS.md` y pruebas de autenticación/autorización |
| Permisos aplicados en backend | Consultas filtradas por usuario o departamento y decisiones restringidas por rol | `backend/app/services/credit_notes.py` y `backend/app/routers/organization.py` |
| Tres módulos funcionales | Organización, Cargos y funciones, y Notas de crédito | Rutas React y endpoints `/organization` y `/credit-notes` |
| Proceso profundo seleccionado: notas de crédito | Creación, aprobación, rechazo, estados terminales y control de versión | Servicio de notas de crédito y pruebas del flujo completo |
| Sin autoaprobación y con rol aprobador distinto | El actor no puede ser el creador ni compartir su rol | Prueba `test_autoapproval_is_rejected_even_for_inconsistent_imported_data` |
| Auditoría de quién hizo cada acción | Evento append-only con nombre y usuario del actor, rol, transición, comentario y fecha | `credit_note_events`, historial visual con estado anterior y nuevo, y pruebas automatizadas |
| Datos suministrados incorporados | Las 25 notas proporcionadas se adaptan al modelo auditable | `NOTES` en `backend/app/seed.py` |
| Base de datos relacional y scripts de creación/carga | SQLite con SQLAlchemy, migración Alembic y seed idempotente | `backend/alembic/versions` y `backend/app/seed.py` |
| Frontend con framework | SPA React + TypeScript + Vite, protegida por sesión | `frontend/src` y scripts de `frontend/package.json` |
| Configuración externa y control de versiones | Variables de entorno de ejemplo, secretos ignorados y commits incrementales | `.env.example`, `.gitignore` e historial Git |
| Registro del uso de IA | Ocho prompts principales; decisiones aceptadas, modificadas y rechazadas; tres errores detectados y guía de defensa en vivo | `docs/AI_USAGE.md` |

## Verificación reproducible

Backend:

```powershell
Set-Location backend
python -m alembic check
python -m pytest -p no:cacheprovider
```

Frontend:

```powershell
Set-Location frontend
npm ci
npm run typecheck
npm test
npm run build
```
