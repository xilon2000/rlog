from typing import Annotated

from fastapi import Depends, Request
import httpx

from app.core.config import settings
from app.core.memory_storage import MemoryStorage
from .services.appendmessage_service import AppendMessageService, create_appendmessage_service


def get_storage(request: Request) -> MemoryStorage:
    return request.app.state.storage

type StorageDep = Annotated[MemoryStorage, Depends(get_storage)]


def get_httpx_async_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.httpx_async_client

type HttpxAsyncClientDep = Annotated[httpx.AsyncClient, Depends(get_httpx_async_client)]


def get_follower_urls() -> tuple[str,...]:
    return settings.follower_urls

type FollowerUrlsDep = Annotated[tuple[str, ...], Depends(get_follower_urls)]


def get_appendmessage_service(
    storage: StorageDep,
    httpx_async_client: HttpxAsyncClientDep,
    follower_urls: FollowerUrlsDep,
) -> AppendMessageService:
    return create_appendmessage_service(
        storage=storage,
        httpx_async_client=httpx_async_client,
        follower_urls=follower_urls
    )

type AppendMessageServiceDep = Annotated[AppendMessageService, Depends(get_appendmessage_service)]
