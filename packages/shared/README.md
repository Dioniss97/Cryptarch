# packages/shared — `@cryptarch/shared`

Paquete **npm** del monorepo con **constantes y contratos** compartidos. El **front** importa desde `@cryptarch/shared`. La **API** (`apps/api/shared_contract.py`) **carga `data/domain.json` al importar** (sin Node) y expone constantes/enums alineados con `src/constants/*.js`.

---

## Inventario clasificado de literales (origen → uso)

| Clase | Literales / valores | Dónde aparecen hoy | En `shared` |
| --- | --- | --- | --- |
| **Roles de usuario** | `admin`, `user` | JWT, guards API (`dependencies.py`), formularios admin, `AuthProvider`, `LoginPage` | `roles.js` + `domain.json` |
| **Estado de documento** | `queued`, `processing`, `indexed`, `error` | Schemas/tests API, futuro worker | `document-status.js` + `domain.json` |
| **Target de filtro guardado** | `user`, `action`, `document` | Enums Pydantic (`SavedFilterTarget`), admin web (filtros) | `saved-filter-target.js` + `domain.json` |
| **Almacenamiento cliente** | `cryptarch_session` | `sessionStore`, tests | `storage.js` + `domain.json` |
| **OAuth2 / token** | `bearer` | Respuesta login API, ejemplos conector | `auth.js` + `domain.json` |
| **Tema UI (preferencias)** | `system`, `light`, `dark` | `PreferencesPanel`, API preferencias | `preferences.js` + `domain.json` |
| **Rutas HTTP** | `/admin/...`, `/chat`, `/me/preferences`, … | `apiClient`, routers FastAPI | **Fuera de shared** (OpenAPI / FastAPI es la verdad) |
| **Rutas SPA (React Router)** | `/admin/users`, `/chat`, … | `router.jsx`, `guards`, links | **Fuera de shared** (solo front; pueden alinearse con paths de API por convención, no por paquete duplicado) |

---

## ¿Hace falta Node/npm en el contenedor de la API?

**No**, si el backend **no importa** el paquete npm. Opciones:

1. **Solo front usa `@cryptarch/shared`** (recomendado para rendimiento y simplicidad de imagen Docker): la imagen de la API sigue siendo solo Python.
2. **Contrato firme para Python**: leer `packages/shared/data/domain.json` en runtime o en tests (el monorepo ya está montado en dev por volumen; en prod copiar ese JSON a la imagen o generar constantes en build). Coste: **despreciable** (un `json.load` puntual o constantes en memoria).
3. **No usar las variables en el back**: válido; mantienes `domain.json` + README como **documentación normativa** y el código Python sigue con strings locales hasta que quieras centralizar.

**Rendimiento**: instalar Node en la API solo para “usar el package” sería mala idea; **no es necesario**. Tampoco penaliza tener el JSON en el repo: no implica ejecutar Node en el contenedor de back.

---

## Estructura

| Ruta | Descripción |
| --- | --- |
| `package.json` | `@cryptarch/shared`, ESM, `exports` → `./src/index.js`. |
| `src/index.js` | Reexporta constantes. |
| `src/constants/*.js` | Módulos por categoría (roles, documentos, etc.). |
| `data/domain.json` | Espejo legible por humanos/scripts/Python; mantener alineado con los `.js`. |

---

## Uso en `apps/web`

```json
"@cryptarch/shared": "file:../../packages/shared"
```

```bash
cd apps/web && npm install
```

```js
import { ROLE_ADMIN, SESSION_STORAGE_KEY } from "@cryptarch/shared";
```

---

## Convenciones

- **Dominio** en `src/constants/`; **contrato multi-runtime** en `data/domain.json`.
- **No** centralizar paths HTTP de la API aquí: FastAPI + OpenAPI.
- Tras cambiar valores de dominio: actualizar **tanto** el `.js` como `domain.json` (o automatizar en el futuro).

---

## Siguiente lectura

- [README raíz](../../README.md), [AGENTS.md](../../AGENTS.md).
- [apps/web/src/shared/](../../apps/web/src/shared/): utilidades **solo front**; este paquete es **compartido normativo** + consumo JS.
