# Checklist de entrega

Usar esta lista antes de compartir el repositorio o generar un archivo ZIP.

## Requisitos funcionales

- [x] Cuatro departamentos con entre 8 y 12 colaboradores ficticios por departamento.
- [x] Cargos, seniority y funciones normalizados.
- [x] Roles Administrador, Jefe de departamento y Colaborador.
- [x] Tres áreas principales por rol: Inicio/Analítica, Estructura organizacional y Notas de crédito.
- [x] Estructura organizacional agrupa colaboradores y cargos en pestañas, conservando rutas y endpoints separados.
- [x] Creación, aprobación y rechazo de notas con estados terminales.
- [x] Segregación de funciones, alcance departamental y prohibición de autoaprobación.
- [x] Auditoría con actor, transición, comentario y fecha.
- [x] Filtros, paginación y resumen de estados según el alcance autenticado.
- [x] Analítica por área, cargo y solicitante visible únicamente para Administrador.

## Datos y backend

- [x] Migraciones de Alembic aplicadas y sincronizadas con los modelos.
- [x] Seed reproducible e idempotente.
- [x] Cuatro departamentos, 33 colaboradores y 25 notas verificados automáticamente.
- [x] Pruebas automatizadas del backend aprobadas.
- [x] OpenAPI y endpoint de salud comprobados con un servidor real.
- [x] Endpoint analítico probado con sesión administrativa y rechazo de otros roles.

Comando de comprobación:

```powershell
.\scripts\verify.ps1 -BackendOnly
```

## Frontend

- [x] Acceso autorizado a `registry.npmjs.org` o registro corporativo equivalente.
- [x] `npm install` finaliza correctamente.
- [x] `frontend/package-lock.json` generado y versionado.
- [x] `npm run typecheck` sin errores.
- [x] `npm test` sin errores.
- [x] `npm run build` genera `frontend/dist`.
- [x] `npm audit` sin vulnerabilidades conocidas.
- [x] Historial visual con actor, fecha y transición explícita de estado.
- [x] Organización muestra departamentos y detalle completo de colaboradores según el alcance del rol.
- [x] Analítica adaptable con filtros, métricas, tendencia y pendientes antiguas.
- [ ] Recorrido manual en navegador con Colaborador, Jefe y Administrador.
- [ ] Diseño revisado en escritorio y vista móvil.

Verificación integral ejecutada desde la raíz:

```powershell
.\scripts\verify.ps1
```

## Seguridad y contenido del repositorio

- [x] `.env`, bases locales, entornos virtuales, herramientas y `node_modules` ignorados.
- [x] Sin credenciales demo fijas en los archivos versionados.
- [x] Contraseñas almacenadas mediante hash y sesiones almacenadas por hash.
- [x] Cookies `HttpOnly`, CSRF y revocación de sesión implementados.
- [x] Decisiones técnicas, permisos, trazabilidad y uso de IA documentados.
- [x] Revisar nuevamente `git status` antes de entregar.
- [x] Confirmar que ningún secreto nuevo fue agregado durante la validación final.

## Uso de Inteligencia Artificial

- [x] Registrar los prompts principales que influyeron en arquitectura, datos, seguridad o experiencia.
- [x] Identificar las sugerencias aceptadas y justificar su adopción.
- [x] Identificar las sugerencias modificadas y explicar el criterio humano aplicado.
- [x] Identificar las sugerencias rechazadas y explicar por qué no eran adecuadas.
- [x] Documentar al menos un error concreto de la IA y la forma en que se detectó y corrigió.
- [x] Relacionar las decisiones con archivos, pruebas y comandos reproducibles.
- [ ] Leer íntegramente `docs/AI_USAGE.md` y ensayar su explicación con palabras propias.

## Git y publicación

Ejecutar primero la auditoría de solo lectura:

```powershell
.\scripts\delivery-audit.ps1
```

- [x] Sustituir la identidad temporal por `Alfonso Medina <alfonso.medina@farmatodo.com>`.
- [x] Corregir la autoría de los commits existentes antes de publicar.
- [x] Crear el repositorio remoto solicitado por el evaluador.
- [x] Configurar `origin` y subir la rama `main`.
- [ ] Abrir el repositorio desde otra sesión o equipo y comprobar que puede clonarse.
- [ ] Confirmar el formato de entrega: enlace, ZIP o ambos.

## Preparación de la presentación

- [ ] Leer `docs/DEMO_GUIDE.md` y ensayar el recorrido completo.
- [ ] Leer `docs/TECHNICAL_DEFENSE.md` y explicar las decisiones con palabras propias.
- [ ] Preparar una solicitud pendiente conocida para mostrar aprobación o rechazo.
- [ ] Tener disponible `http://localhost:8000/docs` como respaldo técnico.
- [ ] Conservar localmente las credenciales generadas por el seed; no publicarlas.
