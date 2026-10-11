from typing import Awaitable, Callable, Optional

import httpx


type CorrelationIdProvider = Callable[[], tuple[Optional[str], Optional[str]]]
type CorrelationIdInjector = Callable[[httpx.Request], Awaitable[None]]

def create_httpx_async_client(
        *, 
        timeout: float=5.0, 
        max_connections: int=100, 
        max_keepalive_connections: int=20,
        keepalive_expiry: int=5,
        correlation_id_provider: CorrelationIdProvider | None = None,
) -> httpx.AsyncClient:   
    event_hooks =  None
    if inject_correlation_id:= _create_correlation_id_injector(correlation_id_provider):
        event_hooks = { "request": [inject_correlation_id] }

    return httpx.AsyncClient(
        timeout=timeout, 
        limits=httpx.Limits(
            max_connections=max_connections,
            max_keepalive_connections=max_keepalive_connections,
            keepalive_expiry=keepalive_expiry,
        ), 
        event_hooks=event_hooks
    )


def _create_correlation_id_injector(
        correlation_id_provider: CorrelationIdProvider | None
) -> CorrelationIdInjector | None:
    if correlation_id_provider:
        async def inject_correlation_id(request: httpx.Request) -> None:
                header_name, correlation_id = correlation_id_provider()
                if header_name and correlation_id:
                    request.headers[header_name] = correlation_id
        return inject_correlation_id
    return None