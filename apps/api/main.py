from fastapi import FastAPI

from admin.routes import router as admin_router
from auth.routes import router as auth_router
from dependencies import get_db

app = FastAPI(title="RAG SaaS API")
app.include_router(auth_router)
app.include_router(admin_router)


@app.get("/health")
def health():
    return {"status": "ok"}
