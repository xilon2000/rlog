from pydantic import BaseModel, Field, StrictStr


class ListMessagesResponse(BaseModel):
    messages: list[StrictStr]


class ReplicateMessageRequest(BaseModel):
    message: StrictStr = Field(min_length=1)


class ReplicateMessageResponse(BaseModel):
    is_succeed: bool
