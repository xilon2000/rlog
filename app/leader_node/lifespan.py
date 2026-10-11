from contextlib import asynccontextmanager
from typing import Optional

from asgi_correlation_id import correlation_id
from fastapi import FastAPI

from app.core.config import settings
from app.core.httpx_async_client import create_httpx_async_client
from app.core.xlogging import configure_logging
from app.core.memory_storage import MemoryStorage


def get_correlation_id() -> tuple[Optional[str], Optional[str]]:
    return settings.correlation_id_header_name, correlation_id.get(None)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.storage = MemoryStorage()
    client = create_httpx_async_client(correlation_id_provider=get_correlation_id)
    async with client:
        app.state.httpx_async_client = client
        yield
