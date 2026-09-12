from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.settings import enable_local_only_defaults

# This runs before the route imports can lazily import faster-whisper and its
# Hugging Face Hub dependency. A local cache miss must become a typed fallback,
# never a Hub cache/version request.
enable_local_only_defaults()

from app.api.routes import router
from app.database import initialize_database
from app.scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(title="Household Agent", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)
