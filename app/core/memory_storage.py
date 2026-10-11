import asyncio


class MemoryStorage:
    def __init__(self):
        self._storage: list[str] = []
        self._lock: asyncio.Lock | None = None

    @property
    def _async_lock(self) -> asyncio.Lock:
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock
    
    async def append_message(self, message: str) -> None:
        async with self._async_lock:
            self._storage.append(message)

    async def list_messages(self) -> list[str]:
        async with self._async_lock:
            return self._storage

