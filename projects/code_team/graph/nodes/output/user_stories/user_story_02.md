# user_story_02 - Gestión y edición de perfil de usuario | Epic: EPIC_01_AUTH

---

**Descripción:**
Como usuario autenticado, quiero poder ver, editar y eliminar mi perfil, para mantener mi información actualizada y ejercer control sobre mis datos.

---

**Contexto Técnico:**
- **Backend:** FastAPI, SQLAlchemy, PostgreSQL, PyJWT
- **Frontend:** React, TailwindCSS, Zustand
- **APIs:** `/api/users/me` (GET/PUT/DELETE)
- **Modelos:** User {id, username, email, password_hash}

---

**Acceptance Criteria:**
- DADO un usuario autenticado, CUANDO accede a su perfil, ENTONCES recibe la información protegida.
- DADO usuario autenticado, CUANDO actualiza datos válidos, ENTONCES cambios reflejados en backend y frontend.
- DADO mail ya existente, CUANDO intenta update, ENTONCES recibe error claro.
- DADO usuario, CUANDO solicita eliminar su cuenta, ENTONCES datos eliminados y sesión invalidada.
- DADO petición sin JWT, ENTONCES responde acceso denegado.

---

**DoD:**
- Código/test >80% coverage
- Documentación API y flujos de edición/borrado
- Validación estricta de cambios (backend y frontend)
- Seguridad: owner sólo edita su perfil, hash pwds, JWT check
- Performance endpoints <200ms.

---

**Escenarios:**
- **Happy path:** Usuario ve y edita username; borra cuenta y sesión cierra.
- **Edge cases:** Update con mail/username en uso; password no válido; request concurrente.
- **Errores:** JWT inválido/ausente; DB caída; inyección update.

---

**Dependencias:**
- Requiere: user_story_01 (login JWT)
- Bloquea: ninguna (habilita mejoras UX pero no bloquea CRUD tareas)

---

**Riesgos:**
- Exposición datos usuario otro – Alto – Scope estricto user_id/JWT, no leaks por id
- Pérdida de sesión/borrado irreversible – Medio – Doble confirmación/alert

---

**Notas:**
- Seguridad profiles: sólo owner puede editar/borrar
- Chequeo validación inputs/outputs
- Feedback visual front sobre update/borrado
- Performance <200ms

---

**Prioridad:** ALTA
- Justificación: Control de usuario vital para confianza y RGPD.

**Story Points:** 5
- BE: 2
- FE: 2
- QA: 1
