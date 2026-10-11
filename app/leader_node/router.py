from fastapi import APIRouter

from .dependencies import AppendMessageServiceDep, StorageDep
from .schemas import (
    AppendMessageRequest, 
    AppendMessageResponse, 
    ListMessagesResponse, 
    make_appendmessage_response
)


router = APIRouter(prefix="/remote_log", tags=["Remote Log API"])


@router.get("/messages", summary="List all messages stored in the leader.")
async def list_messages(storage: StorageDep) -> ListMessagesResponse:
    messages = await storage.list_messages()
    return ListMessagesResponse(messages=messages)


@router.post("/messages", summary="Append a new message to the leader and replicate it to the followers.")
async def append_message(
    body: AppendMessageRequest, 
    appendmessage_service: AppendMessageServiceDep
) -> AppendMessageResponse:
    report = await appendmessage_service.append_message(body.message)
    return make_appendmessage_response(report)
