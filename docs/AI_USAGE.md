# Registro de uso de Inteligencia Artificial

Herramienta principal: OpenAI Codex. Este registro resume interacciones que influyeron materialmente en arquitectura, seguridad o modelo de datos.

## AI-001 — Comprensión del enunciado y selección del proceso

**Prompt resumido:** leer íntegramente el PDF de la prueba, distinguir requisitos obligatorios, revisar los datasets y comenzar con la opción 2 de notas de crédito.

**Sugerencias aceptadas:**

- Elegir notas de crédito por su relación directa con roles, departamentos y trazabilidad.
- Diseñar autorización combinando rol y alcance departamental.
- Tratar el cambio de estado y el evento de auditoría como una sola transacción.
- Mantener Git y este registro desde el comienzo.

**Sugerencias modificadas:**

- Se propuso inicialmente PostgreSQL. Debido a que el entorno no tiene Docker ni servidor PostgreSQL, se inicia con SQLite, que está aceptado por el PDF, manteniendo portabilidad mediante SQLAlchemy y migraciones.

**Sugerencias rechazadas:**

- No se aceptó copiar literalmente el modelo del dataset que omite al actor individual. Esa omisión contradice los requisitos principales de no autoaprobación y auditoría de quién ejecutó la acción.
- No se aceptó almacenar tokens de autenticación en `localStorage`; se diseñó una sesión opaca revocable con cookie `HttpOnly` y protección CSRF.
- No se desactivó la validación TLS cuando Node portátil no reconoció inicialmente la autoridad certificadora del entorno. Se reintentó usando el almacén confiable del sistema; el registro npm devolvió después una prohibición de política (`403`), por lo que no se intentaron mirrors ni rutas que eludieran ese control.

## Ejemplo obligatorio de error o mala práctica detectada

Durante el primer modelo SQLAlchemy, la AI utilizó `mapped_column` para construir la tabla de asociación `position_functions`. Ese constructor está diseñado para atributos de clases declarativas; una instancia directa de `Table` necesita objetos `Column`.

El error no se aceptó por inspección visual: se ejecutó una importación real del módulo y SQLAlchemy produjo `ArgumentError: 'SchemaItem' object ... expected`. Se reemplazaron las dos columnas de asociación por `Column` y se repitió la validación. Este caso reforzó la decisión de importar los modelos y crear el esquema en pruebas, en lugar de asumir que código sintácticamente válido representa un modelo ejecutable.

## AI-002 — Endurecimiento, verificación y preparación de entrega

**Prompt resumido:** continuar el proyecto mientras el registro npm permanecía bloqueado, priorizando trabajo verificable sin dependencias del frontend.

**Sugerencias aceptadas:**

- Añadir filtrado y paginación del lado del servidor, conservando el alcance derivado de la sesión.
- Incorporar un resumen por estado para el dashboard con visibilidad por usuario, departamento o alcance global.
- Probar el seed desde una base vacía, sus cantidades, eventos e idempotencia.
- Centralizar pruebas y comprobación de migraciones en `scripts/verify.ps1`.
- Automatizar la auditoría de entrega y una demostración de API sin persistir credenciales.
- Añadir pruebas de sesión expirada, CSRF, versión obsoleta y ausencia de efectos ante operaciones rechazadas.
- Preparar trazabilidad, guía de API, demostración, defensa técnica y checklist de entrega.

**Correcciones derivadas de la verificación:**

- La primera prueba del seed intentó convertir directamente un `Result` de SQLAlchemy a diccionario. La ejecución real produjo `TypeError`; se materializaron las filas mediante `.all()` y se repitió el verificador hasta obtener éxito.
- Al contrastar la guía de API con los esquemas se detectó que el motivo se recortaba después de validar su longitud. Una cadena de espacios podía superar la longitud mínima y quedar vacía; la normalización se movió antes de las restricciones y se añadió una prueba de regresión.

**Sugerencias rechazadas:**

- No se trató un parser sintáctico de TypeScript como sustituto de `typecheck`, Vitest o el build real.
- No se creó manualmente un `package-lock.json` sin resolver dependencias.
- No se desactivaron TLS, proxy, antivirus ni políticas corporativas, y no se usaron registros alternativos para eludir el `403` de npm.

**Resolución posterior del bloqueo externo:**

Una vez que el acceso al registro oficial fue autorizado, `npm ping` respondió correctamente y `npm install` generó el lockfile real. Se ejecutaron `typecheck`, Vitest, el build de producción y `npm audit`; todas las validaciones finalizaron correctamente y la auditoría reportó cero vulnerabilidades.
