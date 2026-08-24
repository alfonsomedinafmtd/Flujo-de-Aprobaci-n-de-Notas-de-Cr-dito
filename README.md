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

La instalación y los comandos de ejecución se completarán conforme avance el primer corte funcional. Las decisiones y sus motivos se mantienen en [docs/DECISIONS.md](docs/DECISIONS.md).

## Seguridad prevista

- El rol y el departamento se obtienen exclusivamente de la sesión autenticada.
- Las contraseñas se almacenan con un algoritmo de derivación seguro, nunca en texto plano.
- La sesión se transporta en una cookie `HttpOnly` y los cambios de estado requieren protección CSRF.
- Los secretos y la configuración local permanecen fuera del repositorio.
- Las solicitudes y sus eventos de auditoría no admiten eliminación física.

## Estado

Proyecto en construcción. La primera fase define arquitectura, permisos, modelo relacional y trazabilidad del uso de AI antes de implementar los endpoints.

