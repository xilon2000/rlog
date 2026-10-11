from dataclasses import dataclass, asdict

import httpx


@dataclass(frozen=True)
class ReplAppendMessageRequest:
    message: str

    def todict(self):
        return asdict(self)


@dataclass(frozen=True)
class ReplAppendMessageResponse:
    ...


class ReplConnect:
    def __init__(self, httpx_async_client: httpx.AsyncClient):
        self._aclient = httpx_async_client

    async def send_appendmessage_request(self, target_server: str, request: ReplAppendMessageRequest) -> ReplAppendMessageResponse:
        endpoint = f"{target_server.rstrip('/')}/remote_log/replicate_message"
        response = await self._aclient.post(endpoint, json=request.todict())
        response.raise_for_status()
        return ReplAppendMessageResponse()

