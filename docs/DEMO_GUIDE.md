# Guía de demostración

Esta guía propone un recorrido de 8 a 10 minutos por los requisitos principales de la prueba.

## Preparación

En una terminal, iniciar la API:

```powershell
Set-Location backend
..\.venv\Scripts\python.exe -m alembic upgrade head
..\.venv\Scripts\python.exe -m app.seed
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

En otra terminal, después de instalar las dependencias npm:

```powershell
Set-Location frontend
npm run dev
```

Abrir `http://localhost:5173`. Las credenciales se muestran una sola vez cuando el seed crea una base vacía; conservarlas únicamente para la demostración local.

## Demostración alternativa desde PowerShell

Si la API está iniciada, el flujo puede ejecutarse sin guardar contraseñas en archivos ni en el historial de comandos. Desde la raíz del proyecto:

```powershell
.\scripts\demo-api.ps1 -Decision approve -Comment "Soporte validado"
```

Para demostrar un rechazo:

```powershell
.\scripts\demo-api.ps1 -Decision reject -Comment "Soporte documental insuficiente"
```

El script solicita de forma segura las credenciales de un colaborador y de un jefe del mismo departamento o administrador. Luego crea la solicitud, registra la decisión, muestra auditoría y resumen, y revoca ambas sesiones. Este recorrido modifica únicamente la base local de demostración.

## Recorrido sugerido

### 1. Colaborador

1. Iniciar sesión con un colaborador de Cuentas por Cobrar.
2. Mostrar que el dashboard resume solo sus solicitudes.
3. Abrir Estructura organizacional, mostrar su perfil y departamento, y cambiar a la pestaña Cargos y funciones.
4. Usar el acceso directo `Solicitar nota de crédito` del dashboard o del menú y registrar una solicitud.
5. Resaltar que el formulario no permite seleccionar departamento: la API lo deriva de la sesión.
6. Abrir el detalle y señalar el primer evento de auditoría con usuario, fecha y transición `Sin estado → Pendiente`.

### 2. Jefe de departamento

1. Cerrar sesión e ingresar como jefe del mismo departamento.
2. Mostrar el resumen departamental y filtrar las solicitudes pendientes.
3. Abrir la solicitud recién creada.
4. Aprobarla o rechazarla; para demostrar la validación, intentar primero rechazar sin comentario.
5. Mostrar la transición `Pendiente → Aprobada/Rechazada` y el segundo evento de auditoría.
6. Explicar que una solicitud resuelta es terminal y ya no presenta acciones de decisión.

### 3. Administrador

1. Ingresar como administrador.
2. Mostrar que la primera vista es `Analítica` y que no aparece para los otros roles.
3. Recorrer indicadores, montos separados por moneda, áreas, cargos, solicitantes y pendientes antiguas.
4. Aplicar filtros por fecha, departamento y estado; abrir una solicitud desde la tabla de atención requerida.
5. Mostrar que el listado y el directorio tienen alcance global, incluido país, fecha de ingreso, correo ficticio, usuario, rol, cargo y estado.
6. Explicar que el administrador puede decidir globalmente, pero no crear solicitudes ni autoaprobar.

## Evidencias técnicas para mencionar

- El backend nunca acepta rol, usuario creador ni departamento desde el cliente.
- Las consultas aplican alcance por usuario o departamento antes de recuperar datos.
- La cookie de sesión es `HttpOnly`; las operaciones mutables requieren token CSRF.
- Solo se almacena el hash del identificador de sesión.
- La actualización de estado usa versión esperada para evitar decisiones concurrentes.
- La transición y su evento de auditoría se confirman en una misma transacción.
- Los montos utilizan decimal de precisión fija.
- Las migraciones Alembic y el seed permiten reproducir la base.
- La analítica exige `ADMIN` en la API, separa monedas y conserva el cargo histórico del solicitante.

## Validación previa a presentar

```powershell
Set-Location backend
..\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
..\.venv\Scripts\python.exe -m alembic check

Set-Location ..\frontend
npm run typecheck
npm test
npm run build
```

La presentación debe realizarse únicamente cuando todos los comandos terminen sin errores.

## Preguntas que conviene poder responder

- Por qué se eligió notas de crédito como proceso profundo.
- Por qué la autorización vive en el backend y no solo en React.
- Cómo se impide la autoaprobación y el acceso entre departamentos.
- Por qué se utilizó una sesión opaca en lugar de un token en `localStorage`.
- Qué cambiaría para producción: PostgreSQL, rate limiting distribuido, recuperación de contraseña y segundo factor.
- Cómo se adaptaron los datos proporcionados para registrar al creador y al actor de cada decisión.
