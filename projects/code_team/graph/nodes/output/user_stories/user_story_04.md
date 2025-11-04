# user_story_04 - Filtros y búsqueda de tareas | Epic: EPIC_03_UIUX

---

**Descripción:**
Como usuario autenticado, quiero poder buscar y filtrar mis tareas por estado, fecha o texto, para encontrar rápidamente la información relevante.

---

**Contexto Técnico:**
- **Backend:** FastAPI, SQLAlchemy, PostgreSQL
- **Frontend:** React, TailwindCSS, Zustand
- **APIs:** `/api/tasks?status=...&query=...` (GET con filtros)
- **Modelos:** Task {id, user_id, title, description, completed, due_date}

---

**Acceptance Criteria:**
- DADO usuario autenticado, CUANDO aplica filtro estado, ENTONCES sólo tareas filtradas son mostradas.
- DADO usuario autenticado, CUANDO busca por texto, ENTONCES tareas relevantes son listadas.
- DADO filtro sin resultados, ENTONCES UI muestra feedback claro.
- DADO mal input filtro/search, ENTONCES API responde error validado.

---

**DoD:**
- Código/test filtros/search >80% coverage
- Doc frontend/backend filtros-búsqueda
- Validación exhaustiva parámetros
- Seguridad: JWT y sólo tasks del owner
- Performance: <250ms búsqueda, UI <300ms render

---

**Escenarios:**
- **Happy path:** Filtrar/Buscar por estado o texto muestra sólo lo debido.
- **Edge cases:** Query vacía, filtro imposible, input malicioso.
- **Errores:** Parámetros inválidos, DB caída, sin JWT.

---

**Dependencias:**
- Requiere: user_story_03 (CRUD)
- Bloquea: user_story_05 (mejoras UI/performance)

---

**Riesgos:**
- Performance baja en búsquedas grandes – Medio – Mitigación: índice DB, paginación
- XSS en filtro/búsqueda – Medio – Escape frontend, validación backend

---

**Notas:**
- Filtros server y client side coordinados
- UI feedback ante vacío/error
- Performance medido en CI (<250ms backend, <300ms frontend)

---

**Prioridad:** MEDIA
- Justificación: Mejora UX y productividad.

**Story Points:** 3
- BE: 1
- FE: 1
- QA: 1
