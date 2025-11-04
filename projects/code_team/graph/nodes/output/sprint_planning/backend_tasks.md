# Backend Tasks

## user_story_01
- [ ] [US01_BE_01] Crear modelo User (SQLAlchemy, campos: id, username, email, password_hash) `4h`
- [ ] [US01_BE_02] Crear endpoints registro/login/logout/refresh (FastAPI) `5h`
- [ ] [US01_BE_03] Integra JWT authentication y generación tokens `4h`  
- [ ] [US01_BE_04] Validación segura de datos de entrada/salida `2h`
- [ ] [US01_BE_05] Hash y validación de passwords (bcrypt, Passlib) `2h`
- [ ] [US01_BE_06] Rate limit frontend y lógica server-side en login `2h`
- [ ] [US01_BE_07] Tests unitarios y de integración, >80% coverage `5h`
- [ ] [US01_BE_08] Documentación API auth/JWT y escenarios edge `2h`

## user_story_02
- [ ] [US02_BE_01] Endpoint GET/PUT/DELETE `/api/users/me` (User profile) `3h`
- [ ] [US02_BE_02] Validación de updates y duplicado email/username `2h`
- [ ] [US02_BE_03] Propagación de actualización de perfil en JWT `1h`
- [ ] [US02_BE_04] Borrado seguro user y cascade de datos personales `2h`
- [ ] [US02_BE_05] Tests unitarios/profile e integración JWT `2h`
- [ ] [US02_BE_06] Documentar flujo de user profile `1h`

## user_story_03
- [ ] [US03_BE_01] Crear modelo Task (campos: id, user_id, title, description, completed) `2h`
- [ ] [US03_BE_02] CRUD endpoints /api/tasks (user scoped) `4h`
- [ ] [US03_BE_03] Validación ownership/seguridad JWT en tareas `2h`
- [ ] [US03_BE_04] Lógica y tests edge cases (task ajena, input erróneo) `2h`
- [ ] [US03_BE_05] Tests unitarios e integración (>80%) `3h`
- [ ] [US03_BE_06] Doc endpoints CRUD y ownership flows `1h`

## user_story_04
- [ ] [US04_BE_01] Filtros/search con query params en /api/tasks `2h`
- [ ] [US04_BE_02] Indizar y paginar búsqueda, optimizar performance `1h`
- [ ] [US04_BE_03] Validar/limitar parámetros de búsqueda `1h`
- [ ] [US04_BE_04] Tests unitarios y de integración filtros `1h`
- [ ] [US04_BE_05] Documentar endpoints y querys de búsqueda `0.5h`

## user_story_05
- [ ] [US05_BE_01] Endpoint /api/metrics básico, return UX/perf/stats `1h`
- [ ] [US05_BE_02] Security: solo owner puede consultar métricas `0.5h`
- [ ] [US05_BE_03] Metrics logging en backend y tests `1h`
- [ ] [US05_BE_04] Documentar integración métricas-backend `0.5h`
