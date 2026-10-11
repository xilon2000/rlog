from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.xlogging import configure_logging
from app.core.memory_storage import MemoryStorage


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.storage = MemoryStorage()
    yield
