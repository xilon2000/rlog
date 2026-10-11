import asyncio
from contextlib import asynccontextmanager
from typing import Callable

from fastapi import FastAPI
import httpx

from app.core.memory_storage import MemoryStorage
from app.follower_node.dependencies import get_storage as get_follower_storage
from app.follower_node.main import create_follower_app
from app.leader_node.dependencies import (
    get_storage as get_leader_storage,
    get_follower_urls, 
    get_httpx_async_client
)
from app.leader_node.lifespan import get_correlation_id
from app.leader_node.main import create_leader_app


type FastAPIApplicationFactory = Callable[[], FastAPI]


class DelayedASGITransport(httpx.ASGITransport):
    def __init__(self, delay: float = 0.0, **kwargs):
        super().__init__(**kwargs)
        if delay < 0:
            raise ValueError(f"The delay(={delay}) should be a positive number.")
        self._delay = delay

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        if self._delay > 0:
            await asyncio.sleep(self._delay)
        return await super().handle_async_request(request)


class Transport:
    def __init__(self, raise_app_exceptions: bool = True) -> None:
        self._raise_app_exceptions = raise_app_exceptions
        self._follower_nodes: set[FollowerNode] = set()
        self._delays: dict[FollowerNode, float] = dict()

    def add_follower_node(self, follower_node: FollowerNode) -> None:
        self._follower_nodes.add(follower_node)

    def get_follower_nodes(self) -> set[FollowerNode]:
        return self._follower_nodes
    
    def set_delay(self, follower_node: FollowerNode, delay: float):
        if delay < 0:
            raise ValueError(f"The delay(={delay}) should be a positive number.")
        self._delays[follower_node] = delay

    def remove_delay(self, follower_node: FollowerNode):
        self.set_delay(follower_node, delay=0.0)

    def remove_all_delays(self):
        for follower_node in self._follower_nodes:
            self.remove_delay(follower_node)

    def create_async_client(self, node: NodeBase) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            transport=httpx.ASGITransport(
                app=node.app, 
                raise_app_exceptions=self._raise_app_exceptions,
            ), 
            base_url=node.base_url,
        )

    def create_repl_async_client(self, leader_node: LeaderNode):       
        client = httpx.AsyncClient(
            transport=httpx.ASGITransport(
                app=leader_node.app,
                raise_app_exceptions=self._raise_app_exceptions,
            ),
            base_url=leader_node.base_url,
            mounts={
                follower_node.base_url : DelayedASGITransport(
                    app=follower_node.app,
                    delay=self._delays.get(follower_node, 0.0),
                    raise_app_exceptions=self._raise_app_exceptions
                )
                for follower_node in self._follower_nodes
            },
        )

        header_name, cid = get_correlation_id()
        if header_name and cid:
            client.headers[header_name] = cid
            
        return client

class NodeBase:
    def __init__(self, 
        transport: Transport, 
        node_id: str,
        create_app: FastAPIApplicationFactory
    ):
        self._app = create_app()
        self._transport = transport
        self._node_id = node_id

    @property
    def app(self) -> FastAPI:
        return self._app

    @property
    def base_url(self) -> str:
        return f"http://{self._node_id}"
    
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, NodeBase):
            return False
        return self._node_id == value._node_id

    def __hash__(self) -> int:
        return hash(self._node_id)


class LeaderNode(NodeBase):
    def __init__(self, 
        transport: Transport, 
        node_id: str,
        create_app: FastAPIApplicationFactory=create_leader_app
    ):
        super().__init__(transport, node_id, create_app)

        self._storage = MemoryStorage()
        self._app.dependency_overrides[get_leader_storage] = lambda: self._storage
        self._app.dependency_overrides[get_follower_urls] = self._get_follower_urls

    def _get_follower_urls(self) -> tuple[str, ...]:
        return tuple(follower.base_url for follower in self._transport.get_follower_nodes())
        
    async def list_messages(self) -> list[str]:
        async with self._transport.create_async_client(self) as client:
            response: httpx.Response = await client.get("/remote_log/messages")
            response.raise_for_status()
            messages = response.json()["messages"]
            return messages

    async def append_message(self, message: str) -> None:
        async with self.set_repl_client_dependency():
            async with self._transport.create_async_client(self) as client:
                response: httpx.Response = await client.post("/remote_log/messages", json={"message": message})
                response.raise_for_status()

    @asynccontextmanager
    async def set_repl_client_dependency(self):
        try:
            self._app.dependency_overrides[get_httpx_async_client] = lambda: self._transport.create_repl_async_client(self)
            yield
        finally:
            self._app.dependency_overrides.pop(get_httpx_async_client, None)


class FollowerNode(NodeBase):
    def __init__(self, 
        transport: Transport, 
        node_id: str,
        create_app: FastAPIApplicationFactory = create_follower_app
    ):
        super().__init__(transport, node_id, create_app)
        
        self._storage = MemoryStorage()
        self._app.dependency_overrides[get_follower_storage] = lambda: self._storage
        
        transport.add_follower_node(self)
            
    async def list_messages(self) -> list[str]:
        async with self._transport.create_async_client(self) as client:
            response: httpx.Response = await client.get("/remote_log/messages")
            response.raise_for_status()
            messages = response.json()["messages"]
            return messages
