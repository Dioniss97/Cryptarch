from contextlib import asynccontextmanager

from adapters.driven.persistence.dev_seed import ensure_dev_admin
from adapters.driving.http.actions.routes import router as actions_router
from adapters.driving.http.admin.routes import router as admin_router
from adapters.driving.http.auth.routes import router as auth_router
from adapters.driving.http.me.routes import router as me_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(_app: FastAPI):
    ensure_dev_admin()
    yield


app = FastAPI(title="RAG SaaS API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(actions_router)
app.include_router(me_router)
app.include_router(admin_router)


@app.get("/health")
def health():
    return {"status": "ok"}
