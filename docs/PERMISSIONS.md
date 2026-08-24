# Matriz de permisos

La API aplicará autorización tanto al endpoint como a la consulta. Conocer un identificador no concede acceso al recurso.

| Recurso / acción | Administrador | Jefe de departamento | Colaborador |
|---|---|---|---|
| Ver departamentos | Todos | El propio | El propio |
| Ver colaboradores | Todos | Los del departamento propio | Perfil propio y directorio limitado del departamento |
| Ver cargos y funciones | Todos | Departamento propio | Solo lectura del departamento propio |
| Crear nota de crédito | No | No | Sí, para el departamento derivado de su sesión |
| Listar notas de crédito | Todas | Departamento propio | Solo las creadas por el usuario |
| Ver historial | Cualquier nota | Notas del departamento propio | Solo notas propias |
| Aprobar o rechazar | Cualquier departamento | Solo departamento propio | No |
| Administrar estructura | Sí | No | No |

## Invariantes de backend

1. Nunca se confía en `user_id`, `role` o `department_id` enviados por el cliente.
2. Un jefe no puede acceder a una nota de otro departamento manipulando la URL.
3. El solicitante no puede decidir su propia solicitud.
4. Solo una solicitud `PENDING` puede cambiar de estado.
5. Una transición y su evento se confirman o revierten juntos.
6. El historial es append-only y no tendrá endpoints de edición o eliminación.
7. Las cantidades monetarias usan decimal de precisión fija, nunca punto flotante.

