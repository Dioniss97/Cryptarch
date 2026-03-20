# Sprint Frontend 03 — Admin + Chat MVP

## 1) Objetivo del sprint frontend
Entregar una base frontend funcional para:
- Administración (`/admin/*`) con navegación y CRUD inicial sobre recursos clave.
- Experiencia de usuario final (`/chat`) con ejecución de acciones en modo stub.
- Sesión autenticada con separación clara entre perfiles `admin` y `user`.

## 2) Alcance (admin + chat MVP con execute stub)
- **Incluido (MVP):**
  - Login con JWT.
  - Shell de admin con secciones principales y tablas/listados.
  - Chat básico con selector/listado de acciones permitidas por usuario.
  - Ejecución de acción vía runtime (`stub-sync`) mostrando resultado y errores.
  - Preferencias de usuario (`theme`, `language`, `table_density`) aplicadas en UI.
- **Fuera de alcance en este sprint:**
  - Diseño visual avanzado y sistema de diseño completo.
  - Streaming de respuesta en chat.
  - Ejecución real contra integraciones externas (solo stub).

## 3) Arquitectura frontend implementada (carpetas/capas)
Estructura aplicada en `apps/web/src`:

- `app/`
  - `router.jsx` definición de rutas y guards.
  - `AuthProvider.jsx` sesión y estado auth.
- `modules/`
  - `auth/LoginPage.jsx` (login + redirección por rol).
  - `admin/` (`AdminLayout`, `CrudPage`, `TagPicker`, configuración por recurso).
  - `chat/ChatPage.jsx` (schema loader + execute + resultado).
  - `preferences/PreferencesPanel.jsx` (`GET/PATCH /me/preferences`).
- `shared/`
  - `apiClient.js` cliente HTTP centralizado.
  - `sessionStore.js` persistencia en `localStorage`.
  - `ui.jsx` componentes reutilizables de hardening.
  - `styles.css` estilos base sin librería pesada.

Capas lógicas:
- **Presentación:** páginas, layouts y componentes.
- **Aplicación frontend:** hooks/casos de uso por módulo.
- **Infraestructura cliente:** cliente HTTP, mapeo de DTOs, storage.

## 4) Mapa de rutas (`/login`, `/admin/*`, `/chat`) y guards
- `/login`
  - Pública.
  - Redirige a `/admin` o `/chat` si ya hay sesión activa.
- `/admin/*`
  - Guard: `RequireAuth` + `RequireRole('admin')`.
  - Subrutas MVP: `users`, `tags`, `filters`, `groups`, `connectors`, `actions`, `documents`.
- `/chat`
  - Guard: `RequireAuth`.
  - Permitida para `user` y `admin`; UX orientada a usuario final.

Política de redirección:
- Sin token -> `/login`.
- Token inválido/expirado -> limpiar sesión y enviar a `/login`.
- Usuario no admin en `/admin/*` -> redirigir a `/chat`.

## 5) Componentes base reutilizables
- `RequireAuth` y `RequireAdmin`: guards de autenticación y rol.
- `StatusBadge`: etiquetas de estado (`indexed`, `processing`, `error`, etc.).
- `ApiErrorBanner`: representación homogénea de errores API (`detail` y `error.code`).
- `LoadingBlock`: estado de carga visual.
- `EmptyState`: estado vacío reutilizable.
- `ConfirmDelete`: confirmación simple de operaciones destructivas.
- `TagPicker`: multiselección de tags para filtros (semántica AND en UI).
- `CrudPage`: motor CRUD básico reutilizado por recursos admin.

## 6) Contratos backend consumidos (auth/admin/preferences/runtime actions)
Base URL actual: mismo host del API (sin prefijo `/api`).

### Auth
- `POST /auth/login`
  - Body: `{ tenant_id, email, password }`
  - 200: `{ access_token, token_type }`
  - 401: credenciales inválidas.
- `POST /auth/logout`
  - 204 sin body.

### Admin
- `GET /admin/me` -> usuario actual (`sub`, `tenant_id`, `role`).
- CRUD disponibles por recurso:
  - `/admin/users`
  - `/admin/tags`
  - `/admin/filters`
  - `/admin/groups`
  - `/admin/connectors`
  - `/admin/actions`
  - `/admin/documents`
- Patrón soportado: `GET list`, `GET by id`, `POST create`, `PATCH update`, `DELETE`.

### Preferences
- `GET /me/preferences`
- `PATCH /me/preferences`
  - Campos soportados: `language`, `theme` (`system|light|dark`), `table_density` (`comfortable|compact`), `metadata`.

### Runtime actions (chat)
- `GET /actions/{action_id}/input-schema`
  - Devuelve `action_id`, `input_schema_version`, `input_schema_json`.
- `POST /actions/{action_id}/execute`
  - Body: `{ payload: {...} }`
  - Respuesta actual stub: `ok`, `action_id`, `result.mode = "stub-sync"`, `result.echo.payload`.
  - 422 de validación con `error.code = "VALIDATION_ERROR"` y `details`.

## 7) Política de manejo de errores y estados UI
- Estado estándar por pantalla: `loading`, `success`, `empty`, `error`.
- Errores de red/5xx: toast global + bloque de error en vista.
- `401`: logout forzado y redirección a `/login`.
- `403`: vista de acceso denegado (sin romper navegación).
- `404`: fallback contextual ("recurso no encontrado").
- `422`: mostrar errores de validación por campo y/o panel estructurado.
- Reintento manual en listados y acciones críticas.

## 8) Gaps de contrato detectados + mitigación frontend temporal
- No hay endpoint de listado de acciones permitidas para chat (solo schema/execute por `action_id`).
  - **Mitigación:** en MVP usar lista controlada en frontend (config temporal) o, para admins, reutilizar `/admin/actions`.
- No hay endpoint de historial de conversaciones/chat.
  - **Mitigación:** estado efímero en memoria local del cliente.
- No hay refresh token ni endpoint dedicado de renovación.
  - **Mitigación:** sesión simple con relogin al expirar JWT (detección por 401).
- No hay contrato explícito de paginación/filtros en todos los listados admin.
  - **Mitigación:** tablas MVP con fetch completo y filtrado local cuando sea viable.

## 9) Política de actualización continua (bloque a bloque y sección de cambios)
- Este documento se actualiza al cerrar cada bloque funcional frontend (auth, router/guards, admin base, chat runtime, prefs).
- Cada actualización debe:
  - Ajustar alcance real (hecho/no hecho).
  - Confirmar contratos backend usados y desviaciones.
  - Registrar gaps nuevos y mitigaciones.
- Toda modificación se refleja también en `## Historial de cambios` con fecha y nota breve.

## 10) Checklist DoD frontend
- Rutas `/login`, `/admin/*` y `/chat` operativas con guards.
- Login funcional con persistencia de sesión y logout cliente.
- Shell admin con navegación y al menos una vista CRUD por recurso clave.
- Chat MVP ejecuta `GET input-schema` + `POST execute` y renderiza resultado stub.
- Preferencias de usuario leídas y actualizadas desde `/me/preferences`.
- Manejo uniforme de errores `401/403/404/422/5xx`.
- Componentes base reutilizables creados y usados en al menos dos módulos.
- Documento actualizado tras cada bloque y cambios registrados.

## Historial de cambios
- 2026-03-14: Documento inicial del sprint.
- 2026-03-14: Foundation implementada (`react-router-dom`, guards auth/rol, `AuthProvider`, `sessionStore`, `apiClient` con `VITE_API_BASE_URL` y normalización de errores).
- 2026-03-14: Admin CRUD MVP implementado (`users`, `tags`, `connectors`, `documents`) con `AdminLayout` y `CrudPage` reutilizable.
- 2026-03-14: Filter/group/actions implementados con `TagPicker`, editor `target_type + tags`, bindings `user/action/document_filter_ids`, y edición de `input_schema_json` + `input_schema_version`.
- 2026-03-14: Chat MVP y preferencias implementados (`GET /actions/{id}/input-schema`, `POST /actions/{id}/execute`, formulario dinámico v1, `GET/PATCH /me/preferences`).
- 2026-03-14: Hardening básico y smoke tests añadidos (`StatusBadge`, `ApiErrorBanner`, `LoadingBlock`, `EmptyState`, `ConfirmDelete`, tests Vitest + Testing Library).
- 2026-03-14: DTOs CRUD de admin alineados al contrato backend real (payloads create/update por recurso, `tag_ids` con `TagPicker`, JSON textarea robusto para `auth_config`/`request_config`/`input_schema_json`, y `input_schema_version` numérico).
