# Guía de defensa técnica

Este documento reúne respuestas breves para explicar y defender la solución. Conviene comprender las ideas y expresarlas con palabras propias, no memorizarlas literalmente.

## Resumen de un minuto

> Construí un portal interno de Finanzas con una SPA React y una API FastAPI sobre una base relacional. Elegí un monolito modular porque el alcance no justifica la complejidad operativa de microservicios. El caso profundo es el flujo de notas de crédito: un colaborador crea la solicitud, un jefe de su departamento o un administrador la decide, y el backend impide la autoaprobación. Cada transición genera un evento con actor y fecha dentro de la misma transacción. La autorización combina rol y alcance departamental, la sesión es opaca y revocable en una cookie `HttpOnly`, y las mutaciones sensibles requieren CSRF. SQLite facilita la evaluación local; para producción migraría a PostgreSQL. El backend tiene 21 pruebas automatizadas aprobadas y migraciones sincronizadas.

## Arquitectura

### ¿Cómo está organizada la solución?

La solución tiene tres capas desplegables: React con TypeScript y Vite en el cliente, FastAPI con SQLAlchemy en el servidor y una base de datos relacional. En el backend separé autenticación, organización y notas de crédito en routers, dependencias, servicios, esquemas y modelos. React presenta los permisos, pero FastAPI es la autoridad que vuelve a validar cada operación.

### ¿Por qué un monolito modular y no microservicios?

Los módulos comparten usuarios, departamentos, permisos y una transacción de negocio pequeña. Separarlos en servicios añadiría despliegues, observabilidad, contratos remotos y consistencia distribuida sin aportar valor proporcional. El monolito modular conserva límites claros y permite extraer un módulo más adelante si aparecen necesidades reales de escala o autonomía.

### ¿Dónde viven las reglas de negocio?

Las reglas críticas viven en el backend, principalmente en dependencias de autenticación y en el servicio de notas de crédito. La interfaz oculta acciones no permitidas para mejorar la experiencia, pero nunca se considera una barrera de seguridad.

### ¿Cómo se configura el sistema?

La URL de base de datos, los orígenes CORS, los hosts permitidos, la duración y atributos de la cookie se leen desde variables de entorno. La aplicación rechaza CORS con `*` cuando usa credenciales y exige una cookie `Secure` si el entorno es producción.

## Modelo relacional

### ¿Cómo modelaste la organización?

Un departamento contiene cargos; cada colaborador ocupa un cargo y cada cargo puede asociarse a varias funciones mediante `position_functions`. Las funciones también pueden pertenecer a varios cargos, por lo que esa relación es muchos-a-muchos. La cuenta de usuario tiene relación uno-a-uno con el colaborador y no duplica los datos organizacionales.

### ¿Por qué el departamento se obtiene a través del cargo?

La ruta `usuario → colaborador → cargo → departamento` mantiene una única fuente para la asignación organizacional. Evita inconsistencias como una cuenta y un colaborador asociados a departamentos diferentes.

### ¿Por qué la nota también conserva su departamento solicitante?

Es una instantánea histórica del contexto en que se creó la solicitud. Si el colaborador cambia de cargo después, la nota debe conservar el departamento responsable original. Este dato no lo elige el cliente: el backend lo deriva de la sesión al crear la nota.

### ¿Qué entidades forman el proceso?

`credit_notes` guarda monto, moneda, motivo, creador, departamento solicitante, tienda, compañía, estado, versión y fechas. `credit_note_events` guarda cada acción, actor, estado anterior, estado nuevo, comentario y momento. Tiendas y compañías son catálogos relacionados, no texto repetido en cada solicitud.

### ¿Cómo se manejan los montos?

Se usa `Decimal` y `Numeric(14, 2)`, además de una restricción positiva. No se usa punto flotante porque puede introducir errores binarios de redondeo en valores monetarios.

## Roles y alcance

### ¿Qué puede hacer cada rol?

- `COLLABORATOR`: crea notas para el departamento derivado de su sesión y consulta únicamente las creadas por él.
- `DEPARTMENT_HEAD`: consulta y decide notas de su propio departamento; no crea solicitudes.
- `ADMIN`: tiene visibilidad global y puede decidir notas de cualquier departamento; tampoco crea solicitudes.

### ¿Cómo evitas que el cliente falsifique su rol o departamento?

Los esquemas rechazan campos adicionales y la API no acepta `role`, `user_id` ni `requesting_department_id` para crear una nota. El usuario, rol y departamento se reconstruyen en el servidor desde la sesión y las relaciones de base de datos.

### ¿El control se aplica solo al endpoint?

No. Las condiciones de alcance se incorporan a las consultas de listado, resumen y detalle. Un jefe filtra por departamento; un colaborador, por creador; un administrador no añade filtro. Conocer o manipular un identificador no concede acceso.

### ¿Por qué una nota ajena responde `404` y no `403`?

El detalle se busca dentro del alcance autorizado. Si no aparece, devuelve `404`, lo que evita confirmar que existe un identificador perteneciente a otro departamento.

### ¿Cómo impides la autoaprobación?

Solo jefe y administrador pueden decidir. Además, el servicio comprueba que el actor no sea el creador y que su rol sea distinto al del solicitante. Es una validación de backend y está cubierta incluso ante un dato importado inconsistente.

## Autenticación y sesiones

### ¿Por qué una sesión opaca en vez de un JWT en `localStorage`?

La sesión opaca permite revocación inmediata: al cerrar sesión se marca el registro como revocado. El navegador solo recibe un valor aleatorio y la base conserva su hash. Un JWT autocontenido suele seguir válido hasta expirar si no se añade infraestructura de revocación; guardarlo en `localStorage` también facilita su extracción ante XSS. Esto no significa que todo JWT sea incorrecto, sino que para este portal la sesión de servidor es más simple y controlable.

### ¿Cómo se protege la cookie?

La cookie es `HttpOnly`, para que JavaScript no lea el identificador; `SameSite=Lax`, para reducir envíos entre sitios; y `Secure` obligatoria en producción, para enviarla solo por HTTPS. CORS acepta únicamente orígenes configurados y también se validan hosts permitidos.

### ¿Qué se almacena en la base de datos?

Se almacena el SHA-256 del identificador aleatorio de sesión, no el valor que viaja en la cookie. También se guardan el hash del token CSRF, expiración, creación y posible revocación. Si se filtrara la tabla, esos hashes no serían directamente cookies utilizables.

### ¿Cómo vence o se revoca una sesión?

Cada petición autenticada comprueba que la sesión exista, no esté revocada y no haya expirado. El cierre de sesión requiere CSRF, marca `revoked_at` y elimina la cookie. También se rechaza la sesión si la cuenta, el colaborador, el cargo o el departamento están inactivos.

## CSRF y seguridad web

### ¿Por qué hace falta CSRF si la cookie es `HttpOnly`?

`HttpOnly` impide leer la cookie desde JavaScript, pero el navegador todavía puede adjuntarla automáticamente a una solicitud. Para mutaciones sensibles, el cliente debe enviar además `X-CSRF-Token`; un sitio externo no conoce ese valor. `SameSite=Lax`, CORS restringido y el token forman defensas complementarias.

### ¿Dónde se guarda el token CSRF?

El valor se mantiene en memoria en la aplicación React; la base conserva solamente su hash. Después del login se entrega uno y, al restaurar una sesión tras recargar la SPA, `/auth/csrf` lo rota. Al rotarlo, el token anterior deja de funcionar.

### ¿Qué protege actualmente el CSRF?

La creación, aprobación, rechazo y cierre de sesión pasan por la dependencia CSRF. Las pruebas comprueban que una creación sin token no cambia la base y que un token anterior falla después de una rotación.

### ¿CSRF sustituye la protección contra XSS?

No. Si un atacante ejecutara JavaScript dentro del origen legítimo podría leer el token mantenido en memoria y operar como el usuario. Por eso siguen siendo necesarias codificación segura de salida, una política CSP, revisión de dependencias y evitar HTML no confiable. CSRF protege frente a solicitudes desde otros sitios, no frente a todo XSS.

## Contraseñas

### ¿Cómo se almacenan?

Se usa `pwdlib` con su configuración recomendada y soporte Argon2. Solo se almacena el hash derivado, nunca la contraseña en texto plano. Argon2 está diseñado para ser costoso en memoria y tiempo, lo que dificulta ataques masivos sobre una base filtrada.

### ¿Cómo evitas revelar si un usuario existe?

El login devuelve el mismo mensaje para usuario desconocido y contraseña incorrecta. Además, verifica un hash ficticio cuando el usuario no existe, reduciendo diferencias evidentes de tiempo entre ambos casos.

### ¿Qué falta para producción en autenticación?

Rate limiting, bloqueo progresivo, MFA, recuperación segura, política de contraseñas, revocación global de sesiones y monitoreo de intentos. Las credenciales del seed son aleatorias, se imprimen al crear la base y son exclusivamente de demostración.

## Auditoría y transacciones

### ¿Qué registra la auditoría?

Cada evento conserva la nota, el actor individual, su acción, estado previo, estado nuevo, comentario y fecha. La creación genera `CREATED`; las decisiones generan `APPROVED` o `REJECTED`. No existen endpoints para modificar o eliminar eventos.

### ¿Por qué una tabla de eventos y no solo `updated_at`?

`updated_at` dice cuándo cambió el registro, pero no quién lo hizo, qué transición ocurrió ni por qué. La tabla de eventos permite reconstruir el proceso y demostrar segregación de funciones.

### ¿Cómo garantizas que el estado y la auditoría no se separen?

La actualización de la nota y la inserción del evento usan la misma sesión y se confirman con un único `commit`. Si la actualización condicional no afecta exactamente una fila, se ejecuta `rollback` y no se agrega el evento. La creación y su primer evento también se confirman juntos.

### ¿La auditoría es absolutamente inmutable?

Es append-only al nivel de la aplicación porque no hay operaciones de edición o eliminación. Un administrador de base de datos todavía podría alterarla. Para mayor garantía en producción añadiría permisos restrictivos, triggers o un registro externo append-only con controles de integridad y retención.

## Estados y concurrencia

### ¿Cuál es la máquina de estados?

Una solicitud nace `PENDING` y puede pasar una sola vez a `APPROVED` o `REJECTED`. Los dos estados finales son terminales. El rechazo exige comentario; la aprobación admite uno opcional.

### ¿Cómo resuelves dos aprobaciones simultáneas?

Se aplica bloqueo optimista. El cliente envía `expected_version` y el servidor ejecuta un `UPDATE` condicionado por identificador, estado `PENDING` y versión esperada. La primera decisión incrementa la versión; la segunda ya no encuentra la combinación original, hace rollback y recibe `409 Conflict`. Así no se generan dos eventos de decisión.

### ¿Por qué no un bloqueo pesimista?

Las colisiones deberían ser poco frecuentes y el bloqueo optimista evita mantener filas bloqueadas durante más tiempo. La actualización condicional es portable y suficiente para esta evaluación. En PostgreSQL también podría evaluarse `SELECT ... FOR UPDATE` si el patrón real de concurrencia lo justificara.

### ¿Qué significan los errores principales?

- `401`: falta una sesión válida o ya expiró.
- `403`: la identidad es conocida, pero falta permiso o el CSRF es inválido.
- `404`: el recurso no existe dentro del alcance del usuario.
- `409`: la nota ya terminó, la vista está desactualizada o otro actor ganó la carrera.
- `422`: el payload o un catálogo no cumple las reglas de validación.

## SQLite y PostgreSQL

### ¿Por qué elegiste SQLite?

El enunciado lo permite y hace que la evaluación sea reproducible sin instalar un servidor ni Docker. SQLAlchemy, tipos portables, claves foráneas activadas y Alembic reducen el acoplamiento al motor.

### ¿Usarías SQLite en producción?

No para un portal con concurrencia real. Migraría a PostgreSQL por su manejo de escrituras concurrentes, bloqueos, observabilidad, respaldo y operación multiusuario. Antes de migrar probaría la migración y las consultas sobre PostgreSQL, porque usar un ORM no garantiza portabilidad perfecta.

### ¿Qué cambiaría al migrar?

La `DATABASE_URL`, el driver y la infraestructura; después se ejecutarían las migraciones y las pruebas contra PostgreSQL. También revisaría enums, fechas UTC, precisión decimal, niveles de aislamiento, índices y el comportamiento de la actualización optimista.

## Seed y adaptación del dataset

### ¿Qué genera el seed?

Genera cuatro departamentos, 33 colaboradores en total y 25 notas adaptadas del dataset: CXC, CXP y TES tienen ocho colaboradores cada uno; PLN tiene ocho más el administrador. También crea cargos, funciones, cuentas, tiendas, compañías y eventos. Las pruebas verifican las cantidades, estados, actores y una segunda ejecución sin duplicados.

### ¿Cómo resolviste la contradicción con el dataset?

El README de los datos omitía identificar solicitante y aprobador, pero el PDF exigía no autoaprobación y auditoría de quién actuó. Priorizé el requisito principal más estricto y añadí creador, departamento y actor a las notas y eventos.

### ¿El seed es una carga productiva?

No. Es una carga reproducible para demostración y pruebas. Si detecta departamentos existentes, no vuelve a insertarlos. Esa protección evita duplicados en el escenario previsto, pero no pretende reparar una carga parcial; en producción usaría migraciones de datos o un proceso de importación transaccional con claves naturales y reportes de errores.

## Estrategia de pruebas

### ¿Qué está automatizado?

El backend tiene 21 pruebas aprobadas. Cubren login y atributos de cookie, errores genéricos, cuentas inactivas, expiración y revocación de sesiones, rotación CSRF, permisos y aislamiento por departamento, creación y decisiones, normalización de entradas, no autoaprobación, comentario de rechazo, auditoría, versión obsoleta, filtros, paginación, resumen, configuración segura y seed idempotente. `alembic check` confirma que modelos y migraciones están sincronizados.

### ¿Qué falta verificar?

El frontend contiene una prueba de permisos y scripts de `typecheck`, pruebas y build, pero su ejecución final está pendiente porque la política de red responde `403` al registro oficial de npm. No se desactivó TLS ni se usaron mirrors para eludir el control. Cuando se habilite el acceso, `scripts/verify.ps1` ejecutará la verificación completa.

### ¿Qué pruebas añadirías después?

Pruebas end-to-end en navegador para el recorrido de los tres roles, pruebas contra PostgreSQL, carga concurrente, accesibilidad, expiración durante una operación, seguridad de cabeceras y restauración ante respaldos.

## Limitaciones y evolución a producción

### ¿Cuáles son las principales limitaciones actuales?

- SQLite es apropiado para evaluación local, no para concurrencia de producción.
- Falta ejecutar el pipeline frontend cuando npm sea accesible y versionar el `package-lock.json` resultante.
- No hay MFA, recuperación de contraseña, rate limiting ni bloqueo temporal.
- No se conserva todavía el historial de cambios de cargo o departamento.
- La auditoría es inmutable desde la API, no frente a un administrador de la base.
- Faltan observabilidad centralizada, alertas, respaldos probados y un proceso formal de gestión de secretos.

### ¿Qué harías antes de desplegar?

Usaría PostgreSQL administrado, HTTPS detrás de un proxy, cookie `Secure`, gestión de secretos, migraciones en CI/CD, dependencias fijadas y escaneadas, rate limiting, MFA según riesgo, CSP y otras cabeceras, logs estructurados sin datos sensibles, métricas, alertas, backups y pruebas de restauración. También ejecutaría pruebas end-to-end y de carga en un entorno similar a producción.

### ¿Cuál sería la primera mejora funcional?

Dependería del usuario de negocio. Candidatas razonables son adjuntar soportes, notificar decisiones, buscar por rangos y responsables, delegar aprobadores con vigencia y registrar cambios organizacionales. No las incluí sin requisitos porque ampliar el alcance habría introducido reglas no acordadas.

## Uso de inteligencia artificial

### ¿Cómo utilizaste IA responsablemente?

La utilicé para analizar requisitos, explorar alternativas, acelerar borradores y revisar riesgos. Las sugerencias que afectaron arquitectura o seguridad quedaron registradas en `docs/AI_USAGE.md`; después se contrastaron con el enunciado, el código ejecutable y pruebas. La decisión final y la responsabilidad sobre la entrega siguen siendo humanas.

### ¿Puedes dar un ejemplo de un error de IA que detectaste?

En un primer modelo se propuso `mapped_column` dentro de una instancia directa de `Table` para la asociación entre cargos y funciones. SQLAlchemy requiere `Column` en ese caso. Una importación real produjo `ArgumentError`, se corrigió el modelo y se repitió la validación. El ejemplo demuestra por qué no basta con aceptar código que parece correcto.

### ¿Qué decisiones sugeridas rechazaste o modificaste?

- Rechacé copiar literalmente el dataset sin actores porque incumplía auditoría y no autoaprobación.
- Rechacé un JWT en `localStorage` y preferí una sesión opaca, revocable y protegida con CSRF.
- Rechacé confiar en rol, usuario o departamento enviados por el cliente.
- Rechacé microservicios para un alcance que puede mantenerse modular dentro de una aplicación.
- Rechacé usar punto flotante para montos y elegí decimal de precisión fija.
- Modifiqué la propuesta inicial de PostgreSQL a SQLite para la evaluación local, dejando documentada la ruta de producción.
- Rechacé desactivar TLS o usar registros alternativos para sortear el bloqueo corporativo de npm.

## Cierre recomendado

> La fortaleza principal no es solo que el flujo funcione, sino que sus invariantes se aplican donde corresponde: en el backend y dentro de transacciones. El sistema deriva el alcance desde la identidad autenticada, evita decisiones duplicadas con versión optimista y deja evidencia de cada acción. También distingo con claridad lo demostrado localmente de lo que aún necesitaría una operación productiva.
