from typing import Literal

from pydantic import BaseModel, Field, StrictStr

from .services.repl_publisher import ReplPublisherReport


class ListMessagesResponse(BaseModel):
    messages: list[StrictStr]


class AppendMessageRequest(BaseModel):
    message: StrictStr = Field(min_length=1)


class SuccessAppendResponse(BaseModel):
    is_succeed: Literal[True] = True


class FailedReplicationModel(BaseModel):
    follower_url: str
    exception: str


class FailedAppendResponse(BaseModel):
    is_succeed: Literal[False] = False
    successful_count: int
    failed_replications: list[FailedReplicationModel]


type AppendMessageResponse = SuccessAppendResponse | FailedAppendResponse


def make_appendmessage_response(report: ReplPublisherReport) -> AppendMessageResponse:
    if report.is_succeed:
        return SuccessAppendResponse()
    
    return FailedAppendResponse(
        is_succeed=False,
        successful_count=report.successful_count,
        failed_replications=[
            FailedReplicationModel(
                follower_url=f.follower_url, 
                exception=str(f.exception)
            )
            for f in report.failed_replications
        ]
    )
