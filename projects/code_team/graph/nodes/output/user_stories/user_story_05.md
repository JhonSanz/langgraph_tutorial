# user_story_05 - UI Polish y métricas UX | Epic: EPIC_04_SECURITY

---

**Descripción:**
Como usuario, quiero contar con una interfaz pulida y métricas básicas de uso, para maximizar la experiencia y el rendimiento de la aplicación.

---

**Contexto Técnico:**
- **Frontend:** React, TailwindCSS, Zustand, uso de React Profiler/ Lighthouse
- **Backend:** FastAPI (exposición endpoint `/api/metrics` básico)
- **UI:** Componentes polidos (button states, loader animado, mensajes error claros)
- **Métricas:** Tiempos carga principal, errores críticos frontend/backend

---

**Acceptance Criteria:**
- DADO usuario navegando, CUANDO la app carga, ENTONCES tiempos de render principales <300ms.
- DADO error grave, ENTONCES usuario ve mensaje claro y feedback para retry.
- DADO Owner, CUANDO visita métricas, ENTONCES puede ver tiempos básicos y errores principales.

---

**DoD:**
- Code FE y BE >80% coverage métricas+UI
- Documentación componentes polish y logs métricas
- Security: no exponer datos sensibles
- Performance: UI <300ms render, endpoints métricas <200ms

---

**Escenarios:**
- **Happy path:** UI carga rápida; métricas visibles owner
- **Edge cases:** Error 404/500; métricas sin datos; buttons estados raros
- **Errores:** Crash UI, endpoint métricas sin datos/carga, feedback pobre

---

**Dependencias:**
- Requiere: user_story_04
- Bloquea: ninguna

---

**Riesgos:**
- Regressión performance FE – Medio – Test+monitor
- Error info leak – Bajo – Endpoint métricas sólo autenticados/owner

---

**Notas:**
- No exponer PII en logs/métricas
- feedback UI visible (loading states, focus states, etc)
- Docs polish y UX guidelines

---

**Prioridad:** BAJA
- Justificación: Mejora gradual, fácil refactor.

**Story Points:** 3
- FE: 2
- BE: 0.5
- QA: 0.5
