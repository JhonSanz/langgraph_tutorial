# user_story_01 - Registro y Login de Usuarios | Epic: EPIC_01_AUTH

---

**Descripción:**
Como usuario visitante, quiero poder registrarme y hacer login en la aplicación, para gestionar mis tareas de forma privada y segura.

---

**Contexto Técnico:**
- **Backend:** FastAPI (Python 3.11), SQLAlchemy, PostgreSQL, PyJWT, Passlib (bcrypt)
- **Frontend:** React (Vite), TailwindCSS, Zustand
- **APIs:** `/api/auth/register`, `/api/auth/login`, `/api/auth/logout`, `/api/auth/refresh`
- **Modelos:** User {id, username, email, password_hash}
- **Seguridad:** JWT firmado corto, passwords hasheadas (bcrypt), validación campos, CORS restrictivo

---

**Acceptance Criteria:**
- DADO un usuario nuevo, CUANDO se registra con datos válidos, ENTONCES recibe confirmación y token JWT válido.
- DADO usuario existente, CUANDO registra con mail usado, ENTONCES recibe error.
- DADO usuario existente, CUANDO login con user/pass válidos, ENTONCES recibe token JWT y acceso a tareas.
- DADO login con datos incorrectos, ENTONCES recibe error claro y no obtiene token.
- DADO token expirado, CUANDO accede, ENTONCES se requiere relogin.

---

**DoD:**
- Código backend/ frontend con cobertura tests >80%
- Revisión de PR y merge seguro
- Documentación endpoints, JWT y flujos registro/login
- Seguridad (OWASP: hashing, rate limit login, input output validation)
- Performance endpoints <200ms bajo carga moderada

---

**Escenarios:**
- **Happy path:** Registro nuevo usuario; login existoso; logout limpia JWT y estado FE/BE.
- **Edge cases:** E-mail inválido, user preexistente, campos vacíos/incorrectos, password débil.
- **Errores:** DB down, JWT corrupto, ataque fuerza bruta (rate limit), CORS mal configurado.

---

**Dependencias:**
- Requiere: Ninguna (inicia cadena de valor)
- Bloquea: user_story_02, user_story_03

---

**Riesgos:**
- Fuga JWT – Impacto: ALTO – Mitigación: expiración corta, secure cookie, servidor sin XSS expuesto
- Password hash débil – Impacto: ALTO – Mitigación: bcrypt con salt
- Registro spam – Impacto: MEDIO – Mitigación: rate limit, captcha simple en BE, validación mail fuerte

---

**Notas:**
- Uso OWASP ASVS nivel 2 criterios autenticación.
- Validación exhaustiva frontend/backend.
- Política de passwords (largo mínimo y check complejidad, error claros).
- JWT almacenado sólo FE, nunca público/URL.
- Performance API <200ms, render login <300ms.

---

**Prioridad:** ALTA
- Justificación: Este flujo es base para toda la app; bloquea acceso a datos y CRUD de tareas.

**Story Points:** 8
- BE: 4 (modelos, endpoints, tests, JWT)
- FE: 3 (formularios, store, validación, tests)
- QA/Review: 1 (test manual, full flow, documentos)
