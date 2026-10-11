import asyncio
from dataclasses import dataclass, field

from .repl_connect import (
    ReplAppendMessageRequest, 
    ReplAppendMessageResponse, 
    ReplConnect,
)


class ReplPublisher:
    def __init__(self, repl_connect: ReplConnect, follower_urls: tuple[str, ...]) -> None:
        self._repl_connect = repl_connect
        self._follower_urls = follower_urls

    async def publish(self, message: str) -> ReplPublisherReport:
        request = ReplAppendMessageRequest(message=message)
        tasks = [
            self._repl_connect.send_appendmessage_request(follower_url, request)
            for follower_url in self._follower_urls
        ]

        results: list[ReplAppendMessageResponse | BaseException] = await asyncio.gather(*tasks, return_exceptions=True)

        report = self._make_report(results)
        return report
    
    def _make_report(self, results: list[ReplAppendMessageResponse | BaseException]) -> ReplPublisherReport:
        report = ReplPublisherReport()
        successful_count = 0

        for follower_url, result in zip(self._follower_urls, results):
            if isinstance(result, BaseException):
                report.failed_replications.append(FailedReplication(follower_url, result))
            elif isinstance(result, ReplAppendMessageResponse):
                successful_count += 1

        report.is_succeed = (len(self._follower_urls) == successful_count)
        report.successful_count = successful_count
        return report


@dataclass
class ReplPublisherReport:
    failed_replications: list[FailedReplication] = field(default_factory=lambda: [], init=False)
    is_succeed: bool = field(default=False, init=False)
    successful_count: int = field(default=0, init=False)


@dataclass
class FailedReplication:
    follower_url: str
    exception: BaseException
    