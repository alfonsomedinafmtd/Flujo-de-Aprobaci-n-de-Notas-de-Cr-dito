# Decisiones técnicas

Este documento se actualiza durante el desarrollo. No pretende reconstruir decisiones al final de la prueba.

## ADR-001: seleccionar el flujo de notas de crédito

**Estado:** aceptada.

Se implementará la opción 2 porque reutiliza naturalmente departamentos y roles, permite demostrar segregación de funciones y produce reglas deterministas que pueden probarse. El detector de anomalías exigiría definir umbrales, ventanas de reincidencia y heurísticas de transposición no especificadas en el enunciado.

El flujo tendrá tres estados: `PENDING`, `APPROVED` y `REJECTED`. Los dos últimos serán terminales. Crear una solicitud generará el primer evento de auditoría; aprobar o rechazar actualizará la solicitud y agregará exactamente un evento dentro de la misma transacción.

## ADR-002: resolver el conflicto entre el PDF y el dataset

**Estado:** aceptada.

El README del dataset afirma que el proceso no necesita identificar al solicitante ni al aprobador. El PDF principal exige impedir la autoaprobación, usar un rol aprobador distinto y auditar quién ejecutó cada acción.

Se adopta la regla más estricta del PDF. El dataset se utilizará como referencia, pero se ampliará con usuario creador, departamento solicitante y actor de cada evento. Copiar el SQL sin estas modificaciones incumpliría el enunciado.

## ADR-003: arquitectura modular en un solo backend

**Estado:** aceptada.

Se usará un monolito modular con una API FastAPI, una aplicación React y una base relacional. Esta escala no justifica microservicios; separar despliegues aumentaría la complejidad sin mejorar los objetivos evaluados.

Los módulos del backend serán autenticación, organización y notas de crédito. Las reglas de autorización vivirán en dependencias y servicios del backend, no únicamente en la interfaz.

La selección concreta del stack responde a estas razones:

- **FastAPI y Pydantic:** permiten expresar contratos y validaciones con tipos de Python, reutilizar dependencias para autenticación y autorización, y generar documentación OpenAPI verificable sin mantener una especificación separada.
- **SQLAlchemy y Alembic:** separan las reglas del dominio del motor de base de datos y proporcionan migraciones reproducibles para crear y evolucionar el esquema relacional.
- **React:** cumple el requisito de usar un framework y encaja con una SPA pequeña basada en vistas y componentes reutilizables. Para este alcance ofrece menos estructura accidental que un framework más amplio y mantiene explícito el consumo de la API.
- **TypeScript:** hace visibles en compilación los contratos de usuarios, permisos, notas y eventos, reduciendo errores entre las respuestas de la API y la interfaz.
- **Vite:** aporta un servidor de desarrollo y un build de producción simples y rápidos, sin añadir configuración de empaquetado que no aporta valor al caso evaluado.

El objetivo no es elegir cada herramienta por popularidad, sino mantener una solución que una sola persona pueda levantar, explicar, probar y modificar durante la evaluación.

## ADR-004: SQLite inicial y portabilidad a PostgreSQL

**Estado:** aceptada con limitación conocida.

SQLite está permitido explícitamente y hace reproducible el proyecto sin Docker, que no está disponible en el entorno inicial. SQLAlchemy, tipos portables y migraciones mantendrán abierta la migración a PostgreSQL.

La aprobación concurrente se protegerá mediante una versión de registro y una actualización condicional. PostgreSQL ofrecería mejores garantías de concurrencia y sería la opción preferida para producción.

## ADR-005: sesión opaca en cookie segura

**Estado:** aceptada.

Se prefiere una sesión aleatoria y revocable sobre almacenar un JWT en `localStorage`. El navegador recibirá una cookie `HttpOnly`, `SameSite=Lax` y `Secure` en producción. Las operaciones mutables requerirán un token CSRF entregado al cliente después del login.

En la base solo se persistirá el hash del identificador de sesión. El cierre de sesión revocará la sesión inmediatamente. Al recargar la SPA, un endpoint autenticado rota el token CSRF; un sitio externo no puede leer su respuesta por la política CORS y la cookie `SameSite` no se envía en un POST cross-site.

## ADR-006: permisos y segregación de funciones

**Estado:** aceptada.

- `COLLABORATOR` crea solicitudes para su propio departamento y consulta únicamente las propias.
- `DEPARTMENT_HEAD` consulta y decide solicitudes de su departamento; no crea solicitudes.
- `ADMIN` tiene visibilidad global y puede decidir solicitudes de cualquier departamento.
- Solo usuarios y colaboradores activos pueden autenticarse.
- El departamento se deriva del cargo del colaborador autenticado y nunca se acepta desde el payload.
- El actor que decide debe ser diferente del creador y pertenecer a un rol distinto.
- El rechazo requiere comentario; la aprobación permite uno opcional.

## ADR-007: analítica administrativa con contexto histórico

**Estado:** aceptada.

Se incorpora una vista analítica exclusiva para `ADMIN`. El backend aplica los filtros y devuelve indicadores, montos por moneda, agrupaciones por departamento, cargo y solicitante, tendencia mensual y solicitudes pendientes antiguas. No se descargan todas las notas al navegador para calcular el reporte y una llamada directa de jefe o colaborador recibe `403`.

Los importes en USD y VES se presentan por separado porque sumarlos produciría un indicador financiero incorrecto sin una tasa de conversión definida. Además, cada nota conserva `requester_position_title` como instantánea del cargo al momento de creación. Consultar únicamente el cargo actual del colaborador modificaría retrospectivamente los reportes cuando ocurra un cambio organizacional.

Para el volumen ficticio de la prueba, las agrupaciones se calculan en el servicio backend después de aplicar los filtros en base de datos. En producción, con mayor volumen, se evaluarían agregaciones SQL, índices adicionales, vistas materializadas o un almacén analítico.

## Limitaciones conocidas iniciales

- No se conservará todavía historial de cambios organizacionales de cargo o departamento.
- No se implementará recuperación de contraseña ni segundo factor en el alcance inicial.
- El corte inicial no incluye rate limiting distribuido ni bloqueo temporal por intentos fallidos; debe incorporarse antes de exponer el login fuera de una red interna controlada.
- SQLite es adecuado para la evaluación local, no la recomendación final para concurrencia de producción.
