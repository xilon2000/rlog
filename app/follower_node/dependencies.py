from typing import Annotated

from fastapi import Depends, Request

from app.core.memory_storage import MemoryStorage


async def get_storage(request: Request) -> MemoryStorage:
    return request.app.state.storage


type StorageDep = Annotated[MemoryStorage, Depends(get_storage)]
