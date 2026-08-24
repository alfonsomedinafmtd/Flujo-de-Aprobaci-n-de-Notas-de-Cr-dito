# Checklist de entrega

Usar esta lista antes de compartir el repositorio o generar un archivo ZIP.

## Requisitos funcionales

- [x] Cuatro departamentos con entre 8 y 12 colaboradores ficticios por departamento.
- [x] Cargos, seniority y funciones normalizados.
- [x] Roles Administrador, Jefe de departamento y Colaborador.
- [x] Módulos Organización, Cargos y funciones, y Notas de crédito.
- [x] Creación, aprobación y rechazo de notas con estados terminales.
- [x] Segregación de funciones, alcance departamental y prohibición de autoaprobación.
- [x] Auditoría con actor, transición, comentario y fecha.
- [x] Filtros, paginación y resumen de estados según el alcance autenticado.

## Datos y backend

- [x] Migración inicial de Alembic aplicada y sincronizada con los modelos.
- [x] Seed reproducible e idempotente.
- [x] Cuatro departamentos, 33 colaboradores y 25 notas verificados automáticamente.
- [x] Pruebas automatizadas del backend aprobadas.
- [x] OpenAPI y endpoint de salud comprobados con un servidor real.

Comando de comprobación:

```powershell
.\scripts\verify.ps1 -BackendOnly
```

## Frontend

- [ ] Acceso autorizado a `registry.npmjs.org` o registro corporativo equivalente.
- [ ] `npm install` finaliza correctamente.
- [ ] `frontend/package-lock.json` generado y versionado.
- [ ] `npm run typecheck` sin errores.
- [ ] `npm test` sin errores.
- [ ] `npm run build` genera `frontend/dist`.
- [ ] Recorrido manual en navegador con Colaborador, Jefe y Administrador.
- [ ] Diseño revisado en escritorio y vista móvil.

Cuando npm esté disponible, ejecutar desde la raíz:

```powershell
.\scripts\verify.ps1
```

## Seguridad y contenido del repositorio

- [x] `.env`, bases locales, entornos virtuales, herramientas y `node_modules` ignorados.
- [x] Sin credenciales demo fijas en los archivos versionados.
- [x] Contraseñas almacenadas mediante hash y sesiones almacenadas por hash.
- [x] Cookies `HttpOnly`, CSRF y revocación de sesión implementados.
- [x] Decisiones técnicas, permisos, trazabilidad y uso de IA documentados.
- [ ] Revisar nuevamente `git status` antes de entregar.
- [ ] Confirmar que ningún secreto nuevo fue agregado durante la validación final.

## Git y publicación

Ejecutar primero la auditoría de solo lectura:

```powershell
.\scripts\delivery-audit.ps1
```

- [ ] Sustituir la identidad temporal `Candidato <candidato@example.invalid>` por la identidad del candidato.
- [ ] Definir si se corregirá la autoría de los commits existentes antes de publicar.
- [ ] Crear el repositorio remoto solicitado por el evaluador.
- [ ] Configurar `origin` y subir la rama `main`.
- [ ] Abrir el repositorio desde otra sesión o equipo y comprobar que puede clonarse.
- [ ] Confirmar el formato de entrega: enlace, ZIP o ambos.

## Preparación de la presentación

- [ ] Leer `docs/DEMO_GUIDE.md` y ensayar el recorrido completo.
- [ ] Leer `docs/TECHNICAL_DEFENSE.md` y explicar las decisiones con palabras propias.
- [ ] Preparar una solicitud pendiente conocida para mostrar aprobación o rechazo.
- [ ] Tener disponible `http://localhost:8000/docs` como respaldo técnico.
- [ ] Conservar localmente las credenciales generadas por el seed; no publicarlas.
