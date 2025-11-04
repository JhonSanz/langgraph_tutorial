# Technical Architecture - test_project

## Backend
- **Framework**: FastAPI
- **ORM**: SQLAlchemy, Alembic (migraciones)
- **DB**: PostgreSQL
- **Auth**: JWT (PyJWT), passlib (bcrypt)
- **API Layer**: OpenAPI docs, endpoints REST
- **Test**: Pytest + pytest-cov

## Frontend
- **Framework**: React (Vite)
- **State**: Zustand
- **UI**: TailwindCSS
- **Test**: React Testing Library, Jest
- **Autenticación**: token JWT en localStorage, refresh seguro

## Componentes Clave
- `/api/auth/*` (registro, login, logout, refresh)
- `/api/tasks/*` (CRUD tareas)
- UI: LoginForm, TaskList, TaskEditor
- Zustand store: authSlice, taskSlice

## APIs y Modelos
- `User`: id, username, email, password_hash
- `Task`: id, title, description, completed, user_id

## Seguridad
- Hash passwords (bcrypt).
- Validación exhaustiva input/output.
- Protección CSRF/JWT con expiración, XSS vía React.
- Test de performance: API <200ms/tarea, FE <300ms render.

## Integración y CI/CD
- Lint/format: black, flake8, prettier
- Docker para despliegue local y prod
