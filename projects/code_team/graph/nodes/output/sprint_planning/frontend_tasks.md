# Frontend Tasks

## user_story_01
- [ ] [US01_FE_01] Crear formulario de registro/login con validaciones `3h`
- [ ] [US01_FE_02] Integrar APIs de autenticación (register, login, logout, refresh) `3h` [dep: US01_BE_02]
- [ ] [US01_FE_03] Gestión de sesión con JWT en state/store (Zustand) `2h`
- [ ] [US01_FE_04] UI feedback: errores, loading, constraints password `1.5h`
- [ ] [US01_FE_05] Testing E2E flujo auth y validación coverage `2h`

## user_story_02
- [ ] [US02_FE_01] Página de perfil (ver/editar/borrar), uso Zustand `2h`
- [ ] [US02_FE_02] Integrar API profile (GET/PUT/DELETE) `2h` [dep: US02_BE_01]
- [ ] [US02_FE_03] Validaciones fuertes en campos y feedback UI/UX `1h`
- [ ] [US02_FE_04] Test unitarios y E2E sobre flows de perfil `1h`

## user_story_03
- [ ] [US03_FE_01] Página/lista de tareas (Zustand + Tailwind) `2h`
- [ ] [US03_FE_02] Form para crear/editar tarea, validación local `1.5h`
- [ ] [US03_FE_03] Integrar APIs CRUD tareas y sincronizar Zustand `2h` [dep: US03_BE_02]
- [ ] [US03_FE_04] Validación ownership, feedback error y loading UX `1h`
- [ ] [US03_FE_05] Pruebas unitarias/E2E lista y CRUD tasks `1.5h`

## user_story_04
- [ ] [US04_FE_01] UI de filtros y búsqueda frontend tasks `1h`
- [ ] [US04_FE_02] Integrar query params API y coordinar search UI `1.5h` [dep: US04_BE_01]
- [ ] [US04_FE_03] Feedback error/empty/filter, validación client-side `1h`
- [ ] [US04_FE_04] Tests filtros y búsqueda FE, edge cases `1h`

## user_story_05
- [ ] [US05_FE_01] Pulir componentes UI (estados, loaders, mensajes claros) `1h`
- [ ] [US05_FE_02] Instrumentar métricas con React Profiler/Lighthouse `1h`
- [ ] [US05_FE_03] Usar endpoint `/api/metrics` y mostrar métricas owner `0.5h` [dep: US05_BE_01]
- [ ] [US05_FE_04] Pruebas rápida de UX (render, feedback, estados) `0.5h`