# apps/web

Frontend en React: chat para usuarios autenticados y panel de administración (rutas bajo `/admin`), con enrutado y guards en `react-router-dom`.

---

## Stack

| Pieza | Versión / notas (según `package.json`) |
| --- | --- |
| React | ^18.3.1 |
| Vite | ^6.0.7 |
| react-router-dom | ^7.13.1 |
| Tests | Vitest + Testing Library + jsdom (`vitest` en `devDependencies`) |
| `@cryptarch/shared` | Paquete monorepo (`file:../../packages/shared`): constantes compartidas; ver [packages/shared/README.md](../../packages/shared/README.md). |

---

## Scripts npm

| Script | Qué hace |
| --- | --- |
| `npm run dev` | Arranca Vite en el puerto **3000** (`vite --port 3000`). |
| `npm run build` | Build de producción (`vite build`). |
| `npm run preview` | Sirve el build generado. |
| `npm test` | Ejecuta tests una vez (`vitest run`). |
| `npm run test:watch` | Vitest en modo watch. |
| `npm run format` | Formatea con Prettier (`src/` y `packages/shared/src/`). |
| `npm run format:check` | Comprueba formato sin escribir (útil en CI). |
| `npm run lint` | ESLint sobre `src/` y el paquete compartido. |

La configuración de Vite (`vite.config.js`) fija además `server.port: 3000` y `server.host: "0.0.0.0"` (útil en contenedores o red local).

---

## Organización de `src/`

| Carpeta / archivo | Rol |
| --- | --- |
| `app/` | Rutas (`router.jsx`), guards (`guards.jsx`), `AuthProvider.jsx`. |
| `modules/admin/` | UI del panel admin (layout, workspaces, CRUD genérico, etc.). |
| `modules/auth/` | Login. |
| `modules/chat/` | Página de chat. |
| `modules/preferences/` | Preferencias (p. ej. panel). |
| `shared/` | Cliente HTTP (`apiClient.js`), sesión (`sessionStore.js`), utilidades de UI. |
| `test/` | Configuración de tests y pruebas. |
| Raíz | `App.jsx` (router con `createBrowserRouter` + `RouterProvider`), `main.jsx`, `styles.css`. |

---

## Rutas (resumen)

Definidas en `src/app/router.jsx` y montadas desde `src/App.jsx` con `createBrowserRouter`.

- **`/`** → redirección a `/chat`.
- **`/login`** → login; envuelto en `PublicOnly` (solo si no hay sesión acorde a la lógica del guard).
- Rutas bajo **`RequireAuth`**: **`/chat`** → chat de usuario.
- Rutas bajo **`RequireAuth`** + **`RequireAdmin`**: prefijo **`/admin`** con `AdminLayout`. Hijo índice → `/admin/users`. Rutas hijas explícitas incluyen `users`, `connectors`, `documents`, `tags`, `filters`, `groups`; existe además **`/admin/:resource`** como comodín para el recurso genérico.
- Cualquier otra ruta (**`*`**) → redirección a `/chat`.

---

## API (base URL)

En `src/shared/apiClient.js` la base de las peticiones es `import.meta.env.VITE_API_BASE_URL` o, si no está definida, **`http://localhost:8000`**.

---

## Ejecución en local

Desde este directorio (`apps/web`):

```bash
npm install
npm run dev
```

La app quedará disponible en el puerto **3000** (salvo que cambies scripts o `vite.config.js`).

En el monorepo, el flujo recomendado para levantar todo el entorno (incluida la API y servicios) suele documentarse en la raíz del repositorio: ver [README principal](../../README.md).
