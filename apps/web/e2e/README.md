# Smoke E2E (Playwright)

Requiere stack local en marcha (API en `:8000`, web en `:3000`) y seed dev (`admin@dev.local` / `admin`).

```bash
# Desde la raíz del monorepo
docker compose -f infra/docker-compose.dev.yml up -d

# Migraciones (si la tabla user_preferences no existe)
docker compose -f infra/docker-compose.dev.yml exec api alembic upgrade head

# E2E (reutiliza el servidor en :3000 si ya está levantado)
cd apps/web
npm install
npx playwright install chromium
PLAYWRIGHT_SKIP_WEB_SERVER=1 npm run test:e2e
```
