import pytest

from tests.conftest import measure_time
from tests.testharness import FollowerNode, LeaderNode, Transport


@pytest.mark.anyio
async def test_homework_test(
    transport: Transport, 
    leader_node: LeaderNode, 
    follower_nodes: tuple[FollowerNode, FollowerNode]
):
    delay_1, message_1 = 5, "m1"
    transport.set_delay(follower_nodes[0], delay_1)

    async with measure_time() as duration:
        await leader_node.append_message(message_1)
    
    assert duration["elapsed"] == pytest.approx(delay_1, abs=0.5)
    assert await leader_node.list_messages() == [message_1]

    #------------------------------------------------------------

    delay_2, message_2 = 6, "m2"
    transport.set_delay(follower_nodes[1], delay_2)

    async with measure_time() as duration:
        await leader_node.append_message(message_2)

    assert duration["elapsed"] == pytest.approx(delay_2, abs=0.5)
    assert await leader_node.list_messages() == [message_1, message_2]

    #------------------------------------------------------------

    transport.remove_delay(follower_nodes[0])
    transport.remove_delay(follower_nodes[1])

    #------------------------------------------------------------

    message_3 = "m3"

    async with measure_time() as duration:
        await leader_node.append_message(message_3)

    assert duration["elapsed"] == pytest.approx(0.01, abs=0.1)
    assert await leader_node.list_messages() == [message_1, message_2, message_3]
    assert await follower_nodes[0].list_messages() == [message_1, message_2, message_3]
    assert await follower_nodes[1].list_messages() == [message_1, message_2, message_3]


@pytest.mark.skip(reason="Тест не є частиною домашнього завдання")
@pytest.mark.anyio
async def test_leader_node__append_message__appends_message_to_nodes(leader_node: LeaderNode, follower_nodes: tuple[FollowerNode, FollowerNode]):
    message = "one"

    await leader_node.append_message(message)

    assert await leader_node.list_messages() == [message]
    assert await follower_nodes[0].list_messages() == [message]
    assert await follower_nodes[1].list_messages() == [message]


@pytest.mark.skip(reason="Тест не є частиною домашнього завдання")
@pytest.mark.anyio
async def test_leader_node__append_message__follower_nodes_are_called_in_parallel(transport: Transport, leader_node: LeaderNode, follower_nodes: tuple[FollowerNode, FollowerNode]):
    message, delay_1, delay_2 = "one", 1, 2
    transport.set_delay(follower_nodes[0], delay_1)
    transport.set_delay(follower_nodes[1], delay_2)

    async with measure_time() as duration:
        await leader_node.append_message(message)

    assert duration["elapsed"] == pytest.approx(max(delay_1, delay_2), abs=0.5)
