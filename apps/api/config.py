import os

APP_ENV = os.environ.get("APP_ENV", "")

# Solo lectura en desarrollo: tenant y admin de demo (ver dev_seed).
DEV_SEED_TENANT_ID = os.environ.get(
    "DEV_SEED_TENANT_ID", "00000000-0000-4000-8000-000000000001"
)
DEV_ADMIN_EMAIL = os.environ.get("DEV_ADMIN_EMAIL", "admin@dev.local")
DEV_ADMIN_PASSWORD = os.environ.get("DEV_ADMIN_PASSWORD", "admin")

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/appdb",
)
DATABASE_URL_TEST = os.environ.get(
    "DATABASE_URL_TEST",
    "postgresql://postgres:postgres@localhost:5432/appdb_test",
)
JWT_SECRET = os.environ.get("JWT_SECRET", "dev-secret-change-in-production")
JWT_ALGORITHM = "HS256"
