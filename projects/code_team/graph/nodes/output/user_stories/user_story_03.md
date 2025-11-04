# user_story_03 - CRUD de Tareas | Epic: EPIC_02_TASKS

---

**Descripción:**
Como usuario autenticado, quiero poder crear, leer, actualizar y eliminar tareas propias, para organizar mi trabajo diario eficientemente.

---

**Contexto Técnico:**
- **Backend:** FastAPI, SQLAlchemy, PostgreSQL, PyJWT
- **Frontend:** React, TailwindCSS, Zustand
- **APIs:** `/api/tasks` (GET/POST), `/api/tasks/:id` (GET/PUT/DELETE)
- **Modelos:** Task {id, user_id, title, description, completed}
- **Seguridad:** JWT escopado por user_id, validación ownership

---

**Acceptance Criteria:**
- DADO usuario autenticado, CUANDO accede a `/tasks`, ENTONCES sólo ve sus tareas.
- DADO usuario autenticado, CUANDO crea/edita/elimina tarea, ENTONCES DB y UI reflejan el cambio inmediatamente.
- DADO tarea que no es del usuario, CUANDO accede, ENTONCES recibe error 403.
- DADO input inválido, ENTONCES recibe error validado y no muta DB.

---

**DoD:**
- Código/test >80% coverage
- Documentación endpoints CRUD
- Validaciones: ownership, campos, limits
- Seguridad: SQLAlchemy/ORM, input strict, autenticación JWT
- Performance API <200ms operación

---

**Escenarios:**
- **Happy path:** Crear, leer, editar, borrar tareas (UI refleja instantáneo por Zustand)
- **Edge cases:** task demasiado larga/vacía; concurrent modif; acceso por user_id/otros
- **Errores:** JWT inválido/ausente, task no encontrada, DB caída

---

**Dependencias:**
- Requiere: user_story_01 (autenticación/JWT)
- Bloquea: user_story_04 (filtros y búsqueda)

---

**Riesgos:**
- Data leak user → user – Alto – Ownership estricta, tests integración
- Corrupción datos por race-condition – Medio – Transacciones/lock DB

---

**Notas:**
- Todas operaciones JWT owner-scoped
- Validación ext. longitudes, escapes XSS
- Feedback FE inmediato (Zustand, optimistic UI)
- Performance <200ms op normal

---

**Prioridad:** ALTA
- Justificación: Núcleo funcional app, bloquea filtros/mejoras UI.

**Story Points:** 5
- BE: 2
- FE: 2
- QA: 1
