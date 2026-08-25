# Guía práctica de la API

La API de FastAPI se ejecuta localmente en:

```text
http://localhost:8000/api
```

La documentación interactiva está disponible en `http://localhost:8000/docs` y el endpoint de salud es `GET /api/health`.

Los ejemplos siguientes utilizan PowerShell e `Invoke-RestMethod`. Antes de comenzar, define la URL base:

```powershell
$baseUrl = "http://localhost:8000/api"
```

## Sesión, cookie y protección CSRF

El inicio de sesión crea una cookie de sesión llamada `finance_session` por defecto. La cookie es `HttpOnly`, usa `SameSite=Lax` y, en producción, debe enviarse exclusivamente mediante HTTPS con el atributo `Secure`. Su duración predeterminada es de 60 minutos.

`Invoke-RestMethod` puede guardar y reenviar esa cookie mediante `-SessionVariable` y `-WebSession`. No es necesario ni recomendable copiar manualmente su valor.

Además de la cookie, las siguientes operaciones autenticadas están protegidas mediante el encabezado `X-CSRF-Token`:

- Crear una nota de crédito.
- Aprobar o rechazar una nota.
- Cerrar sesión.

El token CSRF se obtiene al iniciar sesión o se renueva mediante `POST /auth/csrf`. Al renovarlo, el token anterior deja de ser válido.

## Autenticación

### Iniciar sesión

`POST /auth/login` recibe un usuario y una contraseña. Sustituye los valores de ejemplo por credenciales locales válidas; no guardes contraseñas reales en el repositorio.

```powershell
$loginBody = @{
    username = "TU_USUARIO"
    password = "TU_CONTRASENA"
} | ConvertTo-Json

$login = Invoke-RestMethod `
    -Method Post `
    -Uri "$baseUrl/auth/login" `
    -ContentType "application/json" `
    -Body $loginBody `
    -SessionVariable apiSession

$csrfToken = $login.csrf_token
$login.user
```

La variable `$apiSession` conserva la cookie. La respuesta también contiene el perfil del usuario y su rol: `ADMIN`, `DEPARTMENT_HEAD` o `COLLABORATOR`.

### Consultar el usuario actual

`GET /auth/me` valida la cookie y devuelve el perfil asociado a la sesión:

```powershell
$currentUser = Invoke-RestMethod `
    -Method Get `
    -Uri "$baseUrl/auth/me" `
    -WebSession $apiSession

$currentUser
```

### Renovar el token CSRF

`POST /auth/csrf` requiere una sesión válida, pero no el token CSRF anterior:

```powershell
$csrfResponse = Invoke-RestMethod `
    -Method Post `
    -Uri "$baseUrl/auth/csrf" `
    -WebSession $apiSession

$csrfToken = $csrfResponse.csrf_token
```

Después de esta operación se debe usar el nuevo valor de `$csrfToken`.

### Cerrar sesión

`POST /auth/logout` revoca la sesión, elimina la cookie y responde con estado `204 No Content`:

```powershell
Invoke-RestMethod `
    -Method Post `
    -Uri "$baseUrl/auth/logout" `
    -WebSession $apiSession `
    -Headers @{ "X-CSRF-Token" = $csrfToken }
```

## Organización

Todos los endpoints de organización requieren una sesión válida. El backend aplica el alcance según el rol y el departamento del usuario; no se debe confiar en filtros del frontend para controlar acceso.

### Departamentos visibles

`GET /organization/departments` devuelve todos los departamentos activos al administrador y únicamente el departamento propio a los demás roles:

```powershell
$departments = Invoke-RestMethod `
    -Method Get `
    -Uri "$baseUrl/organization/departments" `
    -WebSession $apiSession
```

### Perfil organizacional

`GET /organization/profile` devuelve los datos laborales del usuario autenticado, incluido su correo ficticio, fecha de ingreso, usuario y rol del portal:

```powershell
$profile = Invoke-RestMethod `
    -Method Get `
    -Uri "$baseUrl/organization/profile" `
    -WebSession $apiSession
```

### Directorio

`GET /organization/directory` está disponible para los tres roles. Un administrador puede consultar todos los departamentos o usar `department_id`; los demás roles quedan limitados a su propio departamento.

```powershell
$directory = Invoke-RestMethod `
    -Method Get `
    -Uri "$baseUrl/organization/directory?department_id=1" `
    -WebSession $apiSession
```

Para consultar sin filtro:

```powershell
$directory = Invoke-RestMethod `
    -Method Get `
    -Uri "$baseUrl/organization/directory" `
    -WebSession $apiSession
```

### Empleados con detalle

`GET /organization/employees` está permitido para administradores y jefes de departamento. Incluye contacto ficticio, fecha de ingreso, estado, usuario y rol del portal de cada colaborador dentro del alcance autorizado. El rol colaborador recibe `403 Forbidden`.

```powershell
$employees = Invoke-RestMethod `
    -Method Get `
    -Uri "$baseUrl/organization/employees" `
    -WebSession $apiSession
```

También admite `?department_id=1`, sujeto al alcance del usuario.

### Posiciones y funciones

`GET /organization/positions` devuelve posiciones activas, su departamento, seniority y funciones asociadas:

```powershell
$positions = Invoke-RestMethod `
    -Method Get `
    -Uri "$baseUrl/organization/positions" `
    -WebSession $apiSession
```

También admite `?department_id=1`, sujeto al alcance del usuario.

## Notas de crédito

El alcance de consulta se calcula en el backend:

- `COLLABORATOR`: solamente las notas creadas por ese usuario.
- `DEPARTMENT_HEAD`: todas las notas de su departamento.
- `ADMIN`: todas las notas.

### Consultar el catálogo

`GET /credit-notes/catalog` devuelve las tiendas y compañías activas cuyos identificadores se usan al crear una solicitud:

```powershell
$catalog = Invoke-RestMethod `
    -Method Get `
    -Uri "$baseUrl/credit-notes/catalog" `
    -WebSession $apiSession

$catalog.stores
$catalog.companies
```

### Listar, filtrar y paginar

`GET /credit-notes` admite estos parámetros:

- `status`: opcional; `PENDING`, `APPROVED` o `REJECTED`.
- `limit`: entre 1 y 100; valor predeterminado 50.
- `offset`: cero o mayor; valor predeterminado 0.

```powershell
$notesPage = Invoke-RestMethod `
    -Method Get `
    -Uri "$baseUrl/credit-notes?status=PENDING&limit=10&offset=0" `
    -WebSession $apiSession

$notesPage.total
$notesPage.items
```

La respuesta incluye `items`, `total`, `limit` y `offset`.

### Consultar el resumen

`GET /credit-notes/summary` devuelve contadores dentro del alcance del usuario:

```powershell
$summary = Invoke-RestMethod `
    -Method Get `
    -Uri "$baseUrl/credit-notes/summary" `
    -WebSession $apiSession

$summary
```

La respuesta contiene `total`, `pending`, `approved` y `rejected`.

### Crear una nota

`POST /credit-notes` solo está permitido al rol `COLLABORATOR` y requiere CSRF. El departamento solicitante y el creador se obtienen de la sesión; el cliente no puede elegirlos.

```powershell
$createBody = @{
    amount     = "1250.50"
    currency   = "USD"
    reason     = "Ajuste por diferencia de facturación"
    store_id   = $catalog.stores[0].id
    company_id = $catalog.companies[0].id
} | ConvertTo-Json

$createdNote = Invoke-RestMethod `
    -Method Post `
    -Uri "$baseUrl/credit-notes" `
    -ContentType "application/json" `
    -Body $createBody `
    -WebSession $apiSession `
    -Headers @{ "X-CSRF-Token" = $csrfToken }

$noteId = $createdNote.id
$createdNote
```

Reglas principales del payload:

- `amount`: mayor que cero, con hasta 14 dígitos en total y dos decimales.
- `currency`: `USD` o `VES`.
- `reason`: entre 5 y 1000 caracteres.
- `store_id` y `company_id`: identificadores positivos y activos del catálogo.
- No se permiten campos adicionales.

La nota se crea con estado `PENDING`, versión `1` y un primer evento de auditoría `CREATED`.

### Consultar el detalle y el historial

`GET /credit-notes/{note_id}` devuelve la nota, el nombre completo, usuario, correo y rol del solicitante, además de su arreglo `events`. Cada evento identifica con nombre, usuario y rol a la persona que actuó y constituye el historial de creación y decisión:

```powershell
$note = Invoke-RestMethod `
    -Method Get `
    -Uri "$baseUrl/credit-notes/$noteId" `
    -WebSession $apiSession

$note
$note.events
```

Un identificador inexistente o fuera del alcance del usuario responde `404 Not Found`.

### Aprobar una nota

`POST /credit-notes/{note_id}/approve` está permitido a `DEPARTMENT_HEAD` dentro de su departamento y a `ADMIN` globalmente. Requiere CSRF y la versión actual de la nota.

Para decidir con otro usuario, inicia sesión con credenciales de jefe o administrador y guarda su cookie en una variable diferente:

```powershell
$approverLoginBody = @{
    username = "USUARIO_APROBADOR"
    password = "CONTRASENA_APROBADOR"
} | ConvertTo-Json

$approverLogin = Invoke-RestMethod `
    -Method Post `
    -Uri "$baseUrl/auth/login" `
    -ContentType "application/json" `
    -Body $approverLoginBody `
    -SessionVariable approverSession

$approverCsrf = $approverLogin.csrf_token

$pendingNote = Invoke-RestMethod `
    -Method Get `
    -Uri "$baseUrl/credit-notes/$noteId" `
    -WebSession $approverSession

$approveBody = @{
    expected_version = $pendingNote.version
    comment          = "Soporte validado"
} | ConvertTo-Json

$approvedNote = Invoke-RestMethod `
    -Method Post `
    -Uri "$baseUrl/credit-notes/$noteId/approve" `
    -ContentType "application/json" `
    -Body $approveBody `
    -WebSession $approverSession `
    -Headers @{ "X-CSRF-Token" = $approverCsrf }
```

El comentario de aprobación es opcional. La API impide la autoaprobación y exige que aprobador y solicitante pertenezcan a roles distintos.

### Rechazar una nota

`POST /credit-notes/{note_id}/reject` tiene los mismos permisos y controles de versión que la aprobación, pero el comentario es obligatorio:

```powershell
$pendingNote = Invoke-RestMethod `
    -Method Get `
    -Uri "$baseUrl/credit-notes/$noteId" `
    -WebSession $approverSession

$rejectBody = @{
    expected_version = $pendingNote.version
    comment          = "El soporte no coincide con el monto solicitado"
} | ConvertTo-Json

$rejectedNote = Invoke-RestMethod `
    -Method Post `
    -Uri "$baseUrl/credit-notes/$noteId/reject" `
    -ContentType "application/json" `
    -Body $rejectBody `
    -WebSession $approverSession `
    -Headers @{ "X-CSRF-Token" = $approverCsrf }
```

Las decisiones son terminales: una nota aprobada o rechazada no puede volver a procesarse.

### Consultar analítica administrativa

`GET /credit-notes/analytics` está disponible exclusivamente para el rol Administrador. Jefes y colaboradores reciben `403`, incluso si intentan llamar la ruta directamente.

Filtros opcionales:

- `date_from` y `date_to` en formato `YYYY-MM-DD`.
- `department_id` para un área específica.
- `status` con `PENDING`, `APPROVED` o `REJECTED`.

La respuesta incluye contadores, tasas sobre solicitudes resueltas, tiempo promedio de resolución, montos separados por moneda, resultados por departamento, cargo y solicitante, tendencia mensual y hasta ocho solicitudes pendientes antiguas. El cargo corresponde a la instantánea conservada cuando se creó la nota.

Ejemplo:

```powershell
$analytics = Invoke-RestMethod `
    -Uri "$baseUrl/credit-notes/analytics?status=PENDING" `
    -WebSession $session
```

## Referencia rápida de endpoints

| Método | Ruta | Sesión | CSRF | Uso principal |
|---|---|---:|---:|---|
| `GET` | `/health` | No | No | Estado de la API |
| `POST` | `/auth/login` | No | No | Crear una sesión |
| `GET` | `/auth/me` | Sí | No | Consultar usuario actual |
| `POST` | `/auth/csrf` | Sí | No | Rotar el token CSRF |
| `POST` | `/auth/logout` | Sí | Sí | Revocar la sesión |
| `GET` | `/organization/departments` | Sí | No | Departamentos visibles |
| `GET` | `/organization/profile` | Sí | No | Perfil laboral propio |
| `GET` | `/organization/directory` | Sí | No | Directorio con alcance |
| `GET` | `/organization/employees` | Sí | No | Detalle para jefes y administradores |
| `GET` | `/organization/positions` | Sí | No | Posiciones y funciones |
| `GET` | `/credit-notes/catalog` | Sí | No | Tiendas y compañías activas |
| `GET` | `/credit-notes` | Sí | No | Listar, filtrar y paginar |
| `GET` | `/credit-notes/summary` | Sí | No | Contadores por estado |
| `GET` | `/credit-notes/analytics` | Admin | No | Indicadores y agrupaciones administrativas |
| `POST` | `/credit-notes` | Sí | Sí | Crear una solicitud |
| `GET` | `/credit-notes/{note_id}` | Sí | No | Consultar detalle e historial |
| `POST` | `/credit-notes/{note_id}/approve` | Sí | Sí | Aprobar una solicitud |
| `POST` | `/credit-notes/{note_id}/reject` | Sí | Sí | Rechazar una solicitud |

Todas las rutas de la tabla se agregan a `$baseUrl`, que ya contiene `/api`.

## Códigos de error esperados

### `401 Unauthorized`

Indica que no existe una sesión válida. Puede ocurrir por credenciales incorrectas durante el login, ausencia de cookie, sesión vencida o sesión revocada. El login utiliza un mensaje genérico para no revelar si un usuario existe.

### `403 Forbidden`

La sesión es reconocida, pero la operación no está permitida. Ejemplos: cuenta inactiva, rol insuficiente, departamento fuera de alcance, token CSRF ausente o inválido, intento de autoaprobación o intento de crear una solicitud con un rol distinto de colaborador.

### `404 Not Found`

El recurso no existe o no es visible dentro del alcance del usuario. Para las notas de crédito se responde `404` también cuando el identificador pertenece a otro departamento o usuario, evitando revelar su existencia.

### `409 Conflict`

La solicitud entró en conflicto con su estado actual. Ocurre cuando la nota ya fue resuelta, cuando `expected_version` está desactualizado o cuando otro usuario procesó la nota concurrentemente. Se debe volver a consultar el detalle y no repetir automáticamente la decisión.

### `422 Unprocessable Content`

El JSON no satisface el esquema o una regla de validación. Ejemplos: monto no positivo, moneda o estado desconocido, razón demasiado corta, campos adicionales, identificadores de catálogo inválidos, `limit` fuera del rango permitido o rechazo sin comentario. La respuesta incluye detalles por campo cuando la validación proviene del esquema.
