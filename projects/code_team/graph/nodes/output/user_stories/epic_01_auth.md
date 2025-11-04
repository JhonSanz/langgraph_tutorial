# Epic EPIC_01_AUTH: Autenticación y gestión de usuarios

## Business Objective
Permitir el registro, inicio/cierre de sesión y gestión básica de usuarios para garantizar acceso seguro y personalizado a la aplicación de tareas.

## User Stories
- user_story_01 (8 pts): Registro y login de usuarios (MVP)
- user_story_02 (5 pts): CRUD de perfil usuario

## Success Metrics
- >95% usuarios completan registro/login sin error fatal
- Tokens JWT seguros (<0.1% leak reports)
- <2s tiempo desde login hasta dashboard

## Riesgos
- Token JWT robado – Alto – Mitigar restringiendo expiración/refresh, secure cookie
- Password débil – Alto – Forzar validación y hash
