# Epic EPIC_02_TASKS: CRUD y gestión de tareas

## Business Objective
Permitir a los usuarios crear, leer, actualizar y eliminar tareas personales con performance y fiabilidad.

## User Stories
- user_story_03 (5 pts): CRUD de tareas para usuario autenticado
- user_story_04 (3 pts): Filtro y búsqueda de tareas

## Success Metrics
- 99% operaciones CRUD completan <200ms
- 0 pérdida de datos tras update/delete

## Riesgos
- Data leak entre usuarios – Alto – Scoped consultas por user_id, test rigurosos
- Corrupción de datos – Medio – Migraciones y backups
