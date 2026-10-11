import httpx

from app.core.memory_storage import MemoryStorage
from .repl_publisher import ReplPublisher, ReplPublisherReport
from .repl_connect import ReplConnect


class AppendMessageService:
    def __init__(self, storage: MemoryStorage, repl_publisher: ReplPublisher):
        self._storage = storage
        self._repl_publisher = repl_publisher

    async def append_message(self, message: str) -> ReplPublisherReport:
        await self._storage.append_message(message=message)
        report = await self._repl_publisher.publish(message=message)
        return report


def create_appendmessage_service(
    storage: MemoryStorage, 
    httpx_async_client: httpx.AsyncClient, 
    follower_urls: tuple[str, ...],
) -> AppendMessageService:
    repl_connect = ReplConnect(httpx_async_client=httpx_async_client)
    repl_publisher = ReplPublisher(repl_connect=repl_connect, follower_urls=follower_urls)
    service = AppendMessageService(storage=storage, repl_publisher=repl_publisher)
    return service
