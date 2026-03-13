from fastapi import FastAPI

from adapters.driving.http.admin.routes import router as admin_router
from adapters.driving.http.auth.routes import router as auth_router
from adapters.driving.http.auth.routes_actions_runtime import router as runtime_actions_router
from adapters.driving.http.auth.routes_me_preferences import router as me_preferences_router

app = FastAPI(title="RAG SaaS API")
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(me_preferences_router)
app.include_router(runtime_actions_router)


@app.get("/health")
def health():
    return {"status": "ok"}
