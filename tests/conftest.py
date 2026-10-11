from contextlib import asynccontextmanager
import time

import pytest

from tests.testharness import Transport, LeaderNode, FollowerNode


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def transport() -> Transport:
    return Transport()

@pytest.fixture
async def leader_node(transport: Transport) -> LeaderNode:
    return LeaderNode(transport, node_id="leader")

@pytest.fixture
async def follower_nodes(transport: Transport) -> tuple[FollowerNode, FollowerNode]:
    return (
        FollowerNode(transport, node_id="follower-1"),
        FollowerNode(transport, node_id="follower-2"),
    )


@asynccontextmanager
async def measure_time():
    start = time.monotonic()
    measures = {"elapsed": 0.0}
    try:
        yield measures
    finally:
        measures["elapsed"] = time.monotonic() - start
