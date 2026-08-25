# Registro de uso de Inteligencia Artificial

Este documento cumple la sección 5 del enunciado: registra los prompts principales que influyeron en decisiones relevantes, las sugerencias aceptadas, modificadas y rechazadas, y errores concretos de la IA que fueron detectados y corregidos.

## 1. Herramienta, alcance y criterio de uso

- **Herramienta principal:** OpenAI Codex.
- **Usos:** análisis de requisitos, alternativas de arquitectura, implementación, seguridad, pruebas y documentación.
- **Criterio de validación:** ninguna propuesta relacionada con seguridad, modelo de datos o reglas de negocio se aceptó únicamente porque la generó la IA. Cada decisión se contrastó con el PDF, los datos suministrados, la ejecución real y las pruebas automatizadas.
- **Responsabilidad:** la selección final, revisión y defensa del código corresponden al candidato.
- **Privacidad:** no se incluyeron contraseñas, cookies, tokens ni datos productivos en los prompts.

Los textos siguientes conservan la intención de las solicitudes realizadas. Los prompts que agrupan varios mensajes breves se identifican expresamente como **consolidados**; no se pretende reconstruir cada interacción operativa.

## 2. Prompts principales utilizados

### P-01 — Comprensión del enunciado

> “Vamos a trabajar con una prueba que tengo que realizar; entiende todo en el PDF para comenzar a trabajarlo.”

**Por qué fue principal:** estableció que el PDF era la fuente de verdad y que debía separarse lo obligatorio de los datos opcionales.

**Resultado:** se creó la matriz `docs/REQUIREMENTS_TRACEABILITY.md` para vincular cada requisito con código y evidencia.

### P-02 — Selección del proceso profundo

> “Arrancamos con la opción 2 de notas de crédito.”

**Por qué fue principal:** definió el proceso de negocio que debía desarrollarse en profundidad.

**Resultado:** se documentó la elección en `docs/DECISIONS.md` y se implementó la máquina de estados `PENDING → APPROVED | REJECTED`.

### P-03 — Solución completa del proceso (consolidado)

> “Continuar la opción 2 implementando una solución completa: modelo relacional normalizado, login real, roles y alcance departamental en backend, creación y decisión de notas, auditoría visible, seed, pruebas y documentación.”

**Por qué fue principal:** reunió las decisiones estructurales derivadas de las solicitudes sucesivas de continuar el proyecto.

**Resultado:** API FastAPI/SQLAlchemy/Alembic, SPA React/TypeScript/Vite, cuatro departamentos, 33 colaboradores, 25 notas adaptadas y módulos de Organización, Cargos y funciones, y Notas de crédito.

### P-04 — Autorización y seguridad (consolidado)

> “Revisar que el control de acceso no dependa del frontend: validar sesión, rol y departamento en cada operación sensible; impedir autoaprobación, falsificación del departamento y decisiones concurrentes.”

**Por qué fue principal:** determinó invariantes de seguridad y segregación de funciones.

**Resultado:** sesiones opacas en cookie `HttpOnly`, protección CSRF, consultas con alcance, departamento derivado de la sesión, respuesta `404` fuera del alcance y control optimista mediante `version`.

### P-05 — Bloqueo corporativo de npm

> “`npm ping` devuelve `403 Forbidden` por política de seguridad. ¿Podemos continuar y qué debe solicitarse para habilitar el registro oficial?”

**Por qué fue principal:** obligó a decidir cómo continuar sin eludir controles corporativos.

**Resultado:** se avanzó en backend y documentación; no se desactivó TLS, no se usaron mirrors y no se fabricó el lockfile. Tras la habilitación oficial se ejecutaron instalación, typecheck, Vitest, build y auditoría.

### P-06 — Auditoría de requisitos

> “En base al PDF, ¿qué nos faltaría por agregar?”

**Por qué fue principal:** inició una revisión de brechas contra el enunciado.

**Resultado:** se reforzaron la justificación del stack, la transición visible de estados, el detalle organizacional, la trazabilidad y el checklist de entrega.

### P-07 — Información útil en directorios

> “Quiero que al ver el directorio de colaboradores y las notas de crédito se muestre más detalle, como saber quién hizo la solicitud o cualquier dato valioso que se pueda agregar.”

**Por qué fue principal:** cambió los contratos de lectura y la presentación de auditoría.

**Resultado:** la API y la interfaz muestran solicitante, usuario, correo, rol, departamento y actor de cada evento, sin ampliar el alcance permitido por el backend.

### P-08 — Identidad corporativa y solicitud dentro del portal (consolidado)

> “Quiero que salga Planificación Financiera y un mensaje más corporativo. La solicitud de notas de crédito debe estar dentro del portal, no en la portada.”

**Por qué fue principal:** definió la experiencia de entrada y la ubicación correcta de la acción de negocio.

**Resultado:** la portada quedó como acceso corporativo de Planificación Financiera; la creación solo aparece dentro del portal autenticado y únicamente para colaboradores.

## 3. Sugerencias aceptadas, modificadas y rechazadas

| Clasificación | Propuesta de la IA | Decisión final y motivo | Evidencia |
|---|---|---|---|
| Aceptada | Monolito modular con separación por dominios. | Adecuado al alcance; evita complejidad operativa sin perder límites internos. | `backend/app/routers`, `backend/app/services`, ADR-003 en `docs/DECISIONS.md` |
| Aceptada | Modelo normalizado para departamentos, cargos, funciones y colaboradores. | Evita duplicación y representa la relación muchos-a-muchos entre cargos y funciones. | `backend/app/models.py`, `docs/ERD.md` |
| Aceptada | Aplicar rol y alcance departamental en el backend. | La interfaz mejora la experiencia, pero no puede ser la barrera de seguridad. | `backend/app/dependencies.py`, routers, servicio y pruebas de permisos |
| Aceptada | Sesión opaca revocable con cookie `HttpOnly` y CSRF. | Reduce exposición del identificador, permite revocación y protege mutaciones autenticadas. | `backend/app/security.py`, router de autenticación, ADR-005 |
| Aceptada | Guardar transición y evento de auditoría en una transacción. | Impide que el estado cambie sin dejar evidencia del actor y la fecha. | `backend/app/services/credit_notes.py` |
| Aceptada | Usar versión esperada para decidir una nota. | La primera decisión gana y una vista obsoleta recibe `409`, sin duplicar eventos. | campo `version` y prueba de versión obsoleta |
| Modificada | Usar PostgreSQL desde el inicio. | Se cambió a SQLite porque el PDF lo permite y hace reproducible la evaluación local; SQLAlchemy y Alembic conservan una ruta de migración. | ADR-004 y archivos `.env.example` |
| Modificada | Copiar literalmente el dataset opcional. | Se reutilizaron catálogos y notas, pero se añadieron creador, departamento y actor porque los requisitos principales exigen auditoría y no autoaprobación. | ADR-002 y `backend/app/seed.py` |
| Modificada | Permitir que el cliente seleccione el departamento solicitante. | El departamento se deriva del usuario autenticado para impedir falsificación del alcance. | `CreditNoteCreate`, servicio y pruebas de payload |
| Modificada | Mostrar la solicitud en la portada pública. | La portada queda como acceso corporativo; la solicitud está dentro del portal, después de autenticarse, y solo aparece a colaboradores. | `LoginPage.tsx`, `Layout.tsx`, `DashboardPage.tsx` y backend |
| Rechazada | Ocultar botones como única autorización. | Un cliente modificado podría llamar la API; todas las reglas se vuelven a comprobar en el servidor. | pruebas de autorización directa a endpoints |
| Rechazada | Login ficticio mediante selector de rol. | No demostraría identidad ni autorización real; se implementaron usuarios, hashes y sesiones. | modelos, seed y endpoints `/auth` |
| Rechazada | Guardar JWT o sesión en `localStorage`. | Aumenta la exposición ante XSS y complica la revocación inmediata para este alcance. | ADR-005 |
| Rechazada | Omitir al actor porque el dataset no lo incluía. | Contradice la auditoría solicitada y hace imposible demostrar segregación de funciones. | `credit_note_events` e historial visual |
| Rechazada | Desactivar TLS o usar un mirror para evadir el `403` de npm. | El error provenía de una política corporativa y debía resolverse por el canal autorizado. | lockfile generado después de habilitar el registro oficial |
| Rechazada | Fabricar manualmente `package-lock.json`. | Un lockfile solo es evidencia válida cuando npm resuelve realmente las dependencias. | `frontend/package-lock.json` |
| Rechazada | Usar un parser como sustituto de las validaciones del frontend. | La sintaxis aislada no reemplaza TypeScript, Vitest ni el build real. | `scripts/verify.ps1` |

## 4. Errores o malas prácticas de IA detectados y corregidos

### E-01 — Constructor incorrecto en una tabla de asociación

**Respuesta inicial incorrecta:** la IA utilizó `mapped_column` dentro de la instancia directa `Table` llamada `position_functions`.

**Problema:** `mapped_column` corresponde a atributos de clases declarativas; `Table` requiere objetos `Column`.

**Cómo se detectó:** una importación real del modelo produjo `SQLAlchemy ArgumentError`, aunque el archivo parecía sintácticamente válido.

**Corrección:** se reemplazaron ambas definiciones por `Column`, con claves primarias y foráneas con borrado en cascada.

**Evidencia:** `backend/app/models.py`, creación del esquema y 27 pruebas backend aprobadas.

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

- 27 pruebas automatizadas del backend aprobadas.
- Modelos y migración Alembic sincronizados.
- Typecheck de TypeScript aprobado.
- 2 pruebas Vitest aprobadas.
- Build de producción Vite aprobado.
- Auditoría de entrega aprobada.

Comandos reproducibles desde la raíz:

```powershell
.\scripts\verify.ps1
.\scripts\delivery-audit.ps1
```
