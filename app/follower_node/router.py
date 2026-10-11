from fastapi import APIRouter

from .dependencies import StorageDep
from .schemas import (
    ListMessagesResponse,
    ReplicateMessageRequest,
    ReplicateMessageResponse, 
)


router = APIRouter(prefix="/remote_log")


@router.get(
    "/messages",
    summary="List all messages stored in the follower.",
    tags=["Remote Log API"]
)
async def list_messages(storage: StorageDep) -> ListMessagesResponse:
    messages = await storage.list_messages()
    return ListMessagesResponse(messages=messages)


@router.post(
    "/replicate_message", 
    summary="Append a replicated message to the follower.",
    tags=["Replication Subscriber API"],
)
async def replicate_message(
    body: ReplicateMessageRequest, 
    storage: StorageDep
) -> ReplicateMessageResponse:
    await storage.append_message(body.message)
    return ReplicateMessageResponse(is_succeed=True)
