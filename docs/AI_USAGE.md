# Registro de uso de Inteligencia Artificial

Este documento cumple la sección 5 del enunciado: registra los prompts principales que influyeron en decisiones relevantes, las sugerencias aceptadas, modificadas y rechazadas, y errores concretos de la IA que fueron detectados y corregidos.

## 1. Herramienta, alcance y criterio de uso

- **Herramienta principal:** OpenAI Codex.
- **Usos:** análisis de requisitos, alternativas de arquitectura, implementación, seguridad, pruebas y documentación.
- **Criterio de validación:** ninguna propuesta relacionada con seguridad, modelo de datos o reglas de negocio se aceptó únicamente porque la generó la IA. Cada decisión se contrastó con el PDF, los datos suministrados, la ejecución real y las pruebas automatizadas.
- **Responsabilidad:** la selección final, revisión y defensa del código corresponden al candidato.
- **Privacidad:** no se incluyeron contraseñas, cookies, tokens ni datos productivos en los prompts.

Los textos siguientes registran las solicitudes principales realizadas durante el proyecto. Conservan su propósito y las decisiones que motivaron; cuando una entrada reúne varios mensajes sucesivos, se identifica como **consolidada**.

## 2. Prompts principales utilizados

### P-01 — Análisis integral del enunciado

**Tipo:** prompt individual.

> Analiza íntegramente el PDF de la prueba técnica y los archivos de datos adjuntos. Identifica los requisitos obligatorios, las restricciones, los entregables y los criterios de evaluación. Distingue expresamente las instrucciones del enunciado de las decisiones de implementación y de los datos opcionales. Antes de desarrollar, entrega una matriz de trazabilidad que relacione cada requisito con la solución propuesta y su evidencia verificable.

**Decisión que motivó:** utilizar el PDF como fuente de verdad y separar los requisitos obligatorios de las referencias opcionales.

**Resultado verificable:** `docs/REQUIREMENTS_TRACEABILITY.md` vincula cada requisito con su implementación y evidencia.

### P-02 — Definición del proceso de notas de crédito

**Tipo:** prompt individual.

> Desarrolla la opción 2, correspondiente al flujo de aprobación de notas de crédito. Define actores, permisos, datos de entrada, estados, transiciones permitidas, reglas de segregación de funciones y evidencia de auditoría. La propuesta debe impedir la autoaprobación, restringir las decisiones al alcance autorizado y conservar quién ejecutó cada acción y cuándo lo hizo.

**Decisión que motivó:** seleccionar el proceso que debía implementarse con mayor profundidad funcional y técnica.

**Resultado verificable:** `docs/DECISIONS.md` documenta la elección y el sistema implementa `PENDING → APPROVED | REJECTED`.

### P-03 — Arquitectura e implementación completa

**Tipo:** prompt consolidado.

> Diseña e implementa una solución web completa para el proceso seleccionado. Utiliza un modelo relacional normalizado, una API con reglas de negocio en el backend y una interfaz construida con un framework moderno. Incluye autenticación real, autorización por rol y departamento, creación y decisión de solicitudes, auditoría visible, migraciones, carga inicial reproducible, pruebas automatizadas y documentación técnica. Prioriza una arquitectura mantenible y proporcional al alcance de la prueba.

**Decisión que motivó:** definir el alcance técnico y los componentes estructurales del proyecto.

**Resultado verificable:** API FastAPI/SQLAlchemy/Alembic, SPA React/TypeScript/Vite, cuatro departamentos, 33 colaboradores, 25 notas adaptadas y tres módulos funcionales.

### P-04 — Revisión de seguridad y autorización

**Tipo:** prompt consolidado.

> Audita la solución con enfoque de seguridad. Verifica que ninguna regla de autorización dependa exclusivamente del frontend y que el backend derive la identidad, el rol y el departamento desde la sesión autenticada. Cubre acceso fuera de alcance, falsificación de campos, autoaprobación, CSRF, expiración y revocación de sesiones, y decisiones concurrentes. Para cada control, agrega una prueba que demuestre tanto el caso permitido como el rechazo sin efectos secundarios.

**Decisión que motivó:** establecer los invariantes de seguridad y segregación de funciones que debían protegerse en el servidor.

**Resultado verificable:** cookie `HttpOnly`, sesión opaca, CSRF, consultas con alcance, `404` para recursos ajenos y control optimista mediante `version`.

### P-05 — Diagnóstico del bloqueo corporativo de npm

**Tipo:** prompt individual.

> Diagnostica el error `403 Forbidden` devuelto por `npm ping` contra `https://registry.npmjs.org/`. Determina si Node.js y npm están correctamente instalados, diferencia un problema local de una restricción corporativa y redacta la información necesaria para solicitar la habilitación oficial. No desactives TLS, no modifiques controles de seguridad y no utilices registros alternativos para eludir la política. Mientras se resuelve el acceso, identifica tareas verificables que puedan continuar sin instalar dependencias nuevas.

**Decisión que motivó:** continuar el proyecto sin evadir las políticas de seguridad de la organización.

**Resultado verificable:** se avanzó en backend y documentación; tras la habilitación oficial se ejecutaron instalación, typecheck, Vitest, build y auditoría con cero vulnerabilidades.

### P-06 — Análisis de brechas contra el PDF

**Tipo:** prompt individual.

> Compara el estado actual del repositorio con cada requisito del PDF. Clasifica las brechas por prioridad —obligatoria, alta o recomendada— e indica para cada una el archivo afectado, el cambio necesario y la forma de validarlo. No agregues funcionalidades ajenas al alcance como sustituto de requisitos pendientes. Actualiza la trazabilidad y el checklist únicamente cuando exista evidencia ejecutable.

**Decisión que motivó:** revisar de manera sistemática qué elementos faltaban antes de considerar completa la entrega.

**Resultado verificable:** se reforzaron la justificación del stack, las transiciones visibles, el detalle organizacional, la trazabilidad y `docs/DELIVERY_CHECKLIST.md`.

### P-07 — Enriquecimiento de información y trazabilidad visible

**Tipo:** prompt individual.

> Mejora las vistas del directorio de colaboradores y de notas de crédito con información útil para operación y auditoría. En las solicitudes incluye como mínimo quién la creó, usuario, departamento, estado y fechas; en el historial muestra actor, transición y comentario. En el directorio agrega cargo, seniority, correo, país, fecha de ingreso, estado y rol cuando corresponda. Conserva los filtros de alcance del backend y evita exponer información fuera de los permisos de la sesión.

**Decisión que motivó:** ampliar los contratos de lectura sin comprometer la separación de datos por usuario o departamento.

**Resultado verificable:** la API y la interfaz presentan solicitante, usuario, correo, rol, departamento y actor de eventos dentro del alcance autorizado.

### P-08 — Experiencia corporativa y ubicación de la solicitud

**Tipo:** prompt consolidado.

> Ajusta la experiencia visual a la identidad corporativa suministrada. La portada debe identificar a Planificación Financiera, utilizar un mensaje institucional y funcionar únicamente como acceso al portal. Retira de la portada pública cualquier llamado directo para solicitar notas de crédito. Mantén la creación dentro del portal autenticado, visible solo para el rol Colaborador, y conserva en el backend todas las validaciones de identidad, rol y departamento.

**Decisión que motivó:** definir la comunicación institucional de la portada y ubicar la acción de negocio dentro del entorno autenticado.

**Resultado verificable:** `LoginPage.tsx` contiene el acceso corporativo; `Layout.tsx` y `DashboardPage.tsx` exponen la solicitud dentro del portal solo a colaboradores.

### P-09 — Analítica administrativa de notas de crédito

**Tipo:** prompt consolidado.

> Incorpora como primera pestaña del Administrador un dashboard de notas de crédito por área, cargo y persona. Incluye indicadores, filtros y datos útiles para Planificación Financiera. El acceso debe restringirse en el frontend y en el backend, los montos de monedas distintas no deben combinarse y el reporte debe conservar el contexto histórico del solicitante. Agrega pruebas, migración, documentación y una presentación adaptable a escritorio y móvil.

**Decisión que motivó:** ampliar el valor operativo del portal mediante una vista consolidada sin alterar el flujo principal ni exponer información transversal a otros roles.

**Resultado verificable:** ruta `/analytics`, endpoint administrativo, agrupaciones por área/cargo/persona, tendencia, pendientes antiguas, cargo histórico, filtros y pruebas de autorización.

## 3. Sugerencias aceptadas, modificadas y rechazadas

| Clasificación | Propuesta de la IA | Decisión final y motivo | Evidencia |
|---|---|---|---|
| Aceptada | Monolito modular con separación por dominios. | Adecuado al alcance; evita complejidad operativa sin perder límites internos. | `backend/app/routers`, `backend/app/services`, ADR-003 en `docs/DECISIONS.md` |
| Aceptada | Modelo normalizado para departamentos, cargos, funciones y colaboradores. | Evita duplicación y representa la relación muchos-a-muchos entre cargos y funciones. | `backend/app/models.py`, `docs/ERD.md` |
| Aceptada | Aplicar rol y alcance departamental en el backend. | La interfaz mejora la experiencia, pero no puede ser la barrera de seguridad. | `backend/app/dependencies.py`, routers, servicio y pruebas de permisos |
| Aceptada | Sesión opaca revocable con cookie `HttpOnly` y CSRF. | Reduce exposición del identificador, permite revocación y protege mutaciones autenticadas. | `backend/app/security.py`, router de autenticación, ADR-005 |
| Aceptada | Guardar transición y evento de auditoría en una transacción. | Impide que el estado cambie sin dejar evidencia del actor y la fecha. | `backend/app/services/credit_notes.py` |
| Aceptada | Usar versión esperada para decidir una nota. | La primera decisión gana y una vista obsoleta recibe `409`, sin duplicar eventos. | campo `version` y prueba de versión obsoleta |
| Aceptada | Agregar analítica consolidada exclusiva para administradores. | Aporta supervisión global y demuestra agregación de datos sin ampliar el alcance de otros roles. | `/credit-notes/analytics`, `AnalyticsPage.tsx` y pruebas |
| Modificada | Usar PostgreSQL desde el inicio. | Se cambió a SQLite porque el PDF lo permite y hace reproducible la evaluación local; SQLAlchemy y Alembic conservan una ruta de migración. | ADR-004 y archivos `.env.example` |
| Modificada | Copiar literalmente el dataset opcional. | Se reutilizaron catálogos y notas, pero se añadieron creador, departamento y actor porque los requisitos principales exigen auditoría y no autoaprobación. | ADR-002 y `backend/app/seed.py` |
| Modificada | Permitir que el cliente seleccione el departamento solicitante. | El departamento se deriva del usuario autenticado para impedir falsificación del alcance. | `CreditNoteCreate`, servicio y pruebas de payload |
| Modificada | Mostrar la solicitud en la portada pública. | La portada queda como acceso corporativo; la solicitud está dentro del portal, después de autenticarse, y solo aparece a colaboradores. | `LoginPage.tsx`, `Layout.tsx`, `DashboardPage.tsx` y backend |
| Modificada | Agrupar por el cargo actual del colaborador y sumar todos los montos. | Se conserva el cargo al crear la nota y los montos se separan por moneda para evitar cambios retroactivos e indicadores financieros inválidos. | migración `c31f8b42d9a7`, modelo y servicio analítico |
| Rechazada | Ocultar botones como única autorización. | Un cliente modificado podría llamar la API; todas las reglas se vuelven a comprobar en el servidor. | pruebas de autorización directa a endpoints |
| Rechazada | Login ficticio mediante selector de rol. | No demostraría identidad ni autorización real; se implementaron usuarios, hashes y sesiones. | modelos, seed y endpoints `/auth` |
| Rechazada | Guardar JWT o sesión en `localStorage`. | Aumenta la exposición ante XSS y complica la revocación inmediata para este alcance. | ADR-005 |
| Rechazada | Omitir al actor porque el dataset no lo incluía. | Contradice la auditoría solicitada y hace imposible demostrar segregación de funciones. | `credit_note_events` e historial visual |
| Rechazada | Desactivar TLS o usar un mirror para evadir el `403` de npm. | El error provenía de una política corporativa y debía resolverse por el canal autorizado. | lockfile generado después de habilitar el registro oficial |
| Rechazada | Fabricar manualmente `package-lock.json`. | Un lockfile solo es evidencia válida cuando npm resuelve realmente las dependencias. | `frontend/package-lock.json` |
| Rechazada | Usar un parser como sustituto de las validaciones del frontend. | La sintaxis aislada no reemplaza TypeScript, Vitest ni el build real. | `scripts/verify.ps1` |
| Rechazada | Descargar todas las notas y calcular la analítica exclusivamente en React. | Expondría información innecesaria y convertiría el cliente en autoridad del reporte; los filtros y cálculos se ejecutan en el backend protegido. | servicio `analytics.py` y endpoint con `ADMIN` |

## 4. Errores o malas prácticas de IA detectados y corregidos

### E-01 — Constructor incorrecto en una tabla de asociación

**Respuesta inicial incorrecta:** la IA utilizó `mapped_column` dentro de la instancia directa `Table` llamada `position_functions`.

**Problema:** `mapped_column` corresponde a atributos de clases declarativas; `Table` requiere objetos `Column`.

**Cómo se detectó:** una importación real del modelo produjo `SQLAlchemy ArgumentError`, aunque el archivo parecía sintácticamente válido.

**Corrección:** se reemplazaron ambas definiciones por `Column`, con claves primarias y foráneas con borrado en cascada.

**Evidencia:** `backend/app/models.py`, creación del esquema y 29 pruebas backend aprobadas.

### E-02 — Conversión incorrecta de un resultado SQLAlchemy

**Respuesta inicial incorrecta:** una prueba del seed intentó ejecutar `dict(result)` directamente sobre un objeto `Result`.

**Problema:** la ejecución produjo `TypeError`; el resultado todavía no era una secuencia materializada de pares.

**Corrección:** se obtuvieron primero las filas mediante `.all()` y después se construyó el diccionario.

**Evidencia:** `backend/tests/test_seed.py::test_seed_creates_required_dataset_and_is_idempotent`.

### E-03 — Normalización posterior a la longitud mínima

**Respuesta inicial incorrecta:** la validación recortaba el motivo después de comprobar `min_length`.

**Problema:** una cadena formada únicamente por espacios podía superar la longitud mínima y convertirse después en texto vacío.

**Cómo se detectó:** se contrastó el orden de validación del esquema con la guía de API y se agregó un caso de regresión.

**Corrección:** el validador `strip_reason` se ejecuta en modo `before`, por lo que primero normaliza y luego se aplican las restricciones.

**Evidencia:** `backend/app/schemas.py` y `backend/tests/test_credit_notes.py::test_credit_note_creation_rejects_blank_normalized_reason`.

## 5. Criterio humano que prevaleció

1. El requisito principal del PDF prevalece cuando un dataset opcional lo contradice.
2. Una política corporativa de red no se evade para acelerar una instalación.
3. El cliente nunca es autoridad sobre usuario, rol ni departamento.
4. No se agregan reglas de negocio no solicitadas —por ejemplo, aprobaciones por monto, adjuntos o múltiples niveles— sin validarlas con el responsable funcional.
5. El código generado se valida mediante importación, migraciones, pruebas y build; su apariencia no se considera evidencia suficiente.

## 6. Preparación para explicación o modificación en vivo

| Tema que podrían solicitar | Archivo principal | Qué debe poder explicar el candidato |
|---|---|---|
| Modelo normalizado | `backend/app/models.py` y `docs/ERD.md` | Relaciones, claves y por qué el departamento se obtiene mediante el cargo. |
| Login y sesión | router de autenticación y `backend/app/dependencies.py` | Cookie opaca, hash en base de datos, expiración, revocación y CSRF. |
| Rol y alcance | router de organización y servicio de notas | Diferencia entre visibilidad del colaborador, jefe y administrador. |
| Crear una nota | `create_credit_note` | Solo colaborador, departamento derivado de sesión y evento `CREATED` en la misma transacción. |
| Decidir una nota | `decide_credit_note` | Jefe o administrador, no autoaprobación, estado pendiente y versión esperada. |
| Auditoría visible | `CreditNoteDetailPage.tsx` | Actor, transición, comentario y fecha de cada evento. |
| Datos de demostración | `backend/app/seed.py` | Datos ficticios, cantidades comprobadas e idempotencia. |
| Verificación completa | `scripts/verify.ps1` | Qué comprueba cada etapa y cómo interpretar un fallo. |

Ante una modificación en vivo, el procedimiento será: localizar la regla, explicar su ubicación, hacer el cambio mínimo, agregar o ajustar la prueba correspondiente y ejecutar nuevamente el verificador.

## 7. Evidencia final

- 29 pruebas automatizadas del backend aprobadas.
- Modelos y migración Alembic sincronizados.
- Typecheck de TypeScript aprobado.
- 3 pruebas Vitest aprobadas.
- Build de producción Vite aprobado.
- Auditoría de entrega aprobada.

Comandos reproducibles desde la raíz:

```powershell
.\scripts\verify.ps1
.\scripts\delivery-audit.ps1
```
