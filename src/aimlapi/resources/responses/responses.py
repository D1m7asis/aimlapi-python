from __future__ import annotations

import json
from typing import Any, Callable, List, TypeVar

import httpx
from openai import _streaming as _openai_streaming
from openai._utils import is_mapping
from openai.lib.streaming.responses import _responses as streaming_responses
from openai.resources.responses import responses as openai_responses
from openai.resources.responses.responses import *  # noqa: F401, F403

_SyncStreamT = TypeVar("_SyncStreamT", bound="_openai_streaming.Stream[Any]")
_AsyncStreamT = TypeVar("_AsyncStreamT", bound="_openai_streaming.AsyncStream[Any]")


def _normalize_json_stream(data: Any) -> List[dict[str, Any]]:
    """Normalize non-SSE background responses to a list of stream events.

    The AIML API returns JSON bodies when resuming a background response. These
    bodies may contain a full response object and, optionally, a serialized
    ``stream`` array. We convert this into a list of event dicts that always
    begins with ``response.created`` so the upstream streaming state machine
    can construct the initial snapshot before applying later events.
    """

    base_response = data if is_mapping(data) else {}

    events: List[dict[str, Any]]
    if is_mapping(data) and isinstance(data.get("stream"), list):
        events = [
            event for event in data.get("stream", []) if is_mapping(event)
        ]

        seq_start = events[0].get("sequence_number", 0) if events else 0
        if not any(event.get("type") == "response.created" for event in events):
            events.insert(
                0,
                {
                    "type": "response.created",
                    "sequence_number": seq_start,
                    "response": base_response,
                },
            )
    else:
        events = [data]

    normalized: List[dict[str, Any]] = []
    for event in events:
        if not (is_mapping(event) and event.get("type")):
            event = {
                "type": "response.completed",
                "sequence_number": event.get("sequence_number", 0)
                if is_mapping(event)
                else 0,
                "response": base_response,
            }
        elif "response" not in event:
            event = {**event, "response": base_response}

        normalized.append(event)

    if not any(event.get("type") == "response.created" for event in normalized):
        normalized.insert(
            0,
            {
                "type": "response.created",
                "sequence_number": normalized[0].get("sequence_number", 0)
                if normalized
                else 0,
                "response": base_response,
            },
        )

    return normalized


def _patch_sync_stream() -> None:
    if getattr(_openai_streaming.Stream, "_aimlapi_patched", False):
        return

    original_stream = _openai_streaming.Stream.__stream__

    def __stream__(self: _SyncStreamT):  # type: ignore[override]
        cast_to: type[Any] = self._cast_to  # pyright: ignore[reportPrivateUsage]
        response: httpx.Response = self.response
        process_data: Callable[..., Any] = self._client._process_response_data  # pyright: ignore[reportPrivateUsage]

        content_type = response.headers.get("Content-Type", "").lower()
        if "text/event-stream" not in content_type:
            data = json.loads(response.read())
            for event in _normalize_json_stream(data):
                yield process_data(data=event, cast_to=cast_to, response=response)
            response.close()
            return

        yield from original_stream(self)

    __stream__.__name__ = original_stream.__name__
    _openai_streaming.Stream.__stream__ = __stream__
    _openai_streaming.Stream._aimlapi_patched = True  # type: ignore[attr-defined]


def _patch_async_stream() -> None:
    if getattr(_openai_streaming.AsyncStream, "_aimlapi_patched", False):
        return

    original_stream = _openai_streaming.AsyncStream.__stream__

    async def __stream__(self: _AsyncStreamT):  # type: ignore[override]
        cast_to: type[Any] = self._cast_to  # pyright: ignore[reportPrivateUsage]
        response: httpx.Response = self.response
        process_data: Callable[..., Any] = self._client._process_response_data  # pyright: ignore[reportPrivateUsage]

        content_type = response.headers.get("Content-Type", "").lower()
        if "text/event-stream" not in content_type:
            data = json.loads(await response.aread())
            for event in _normalize_json_stream(data):
                yield process_data(data=event, cast_to=cast_to, response=response)
            response.close()
            return

        async for item in original_stream(self):
            yield item

    __stream__.__name__ = original_stream.__name__
    _openai_streaming.AsyncStream.__stream__ = __stream__
    _openai_streaming.AsyncStream._aimlapi_patched = True  # type: ignore[attr-defined]


def _patch_streaming() -> None:
    _patch_sync_stream()
    _patch_async_stream()


_patch_streaming()

_BaseResponseStream = streaming_responses.ResponseStream
_BaseAsyncResponseStream = streaming_responses.AsyncResponseStream


class AIMLResponseStream(_BaseResponseStream):
    def __stream__(self):  # type: ignore[override]
        content_type = self._raw_stream.response.headers.get("Content-Type", "").lower()
        if "text/event-stream" not in content_type:
            cast_to: type[Any] = self._raw_stream._cast_to  # pyright: ignore[reportPrivateUsage]
            process_data = self._raw_stream._client._process_response_data  # pyright: ignore[reportPrivateUsage]

            data = json.loads(self._raw_stream.response.read())
            for event_data in _normalize_json_stream(data):
                parsed_event = process_data(
                    data=event_data, cast_to=cast_to, response=self._raw_stream.response
                )

                events_to_fire = self._state.handle_event(parsed_event)
                for event in events_to_fire:
                    yield event
            self._raw_stream.response.close()
            return

        yield from super().__stream__()


class AIMLAsyncResponseStream(_BaseAsyncResponseStream):
    async def __stream__(self):  # type: ignore[override]
        content_type = self._raw_stream.response.headers.get("Content-Type", "").lower()
        if "text/event-stream" not in content_type:
            cast_to: type[Any] = self._raw_stream._cast_to  # pyright: ignore[reportPrivateUsage]
            process_data = self._raw_stream._client._process_response_data  # pyright: ignore[reportPrivateUsage]

            data = json.loads(await self._raw_stream.response.aread())
            for event_data in _normalize_json_stream(data):
                parsed_event = process_data(
                    data=event_data, cast_to=cast_to, response=self._raw_stream.response
                )
                events_to_fire = self._state.handle_event(parsed_event)
                for event in events_to_fire:
                    yield event
            await self._raw_stream.response.aclose()
            return

        async for item in super().__stream__():
            yield item


# Swap the streaming classes used by the OpenAI responses module so background
# requests that return JSON bodies instead of SSE frames are parsed correctly.
streaming_responses.ResponseStream = AIMLResponseStream  # type: ignore[assignment]
streaming_responses.AsyncResponseStream = AIMLAsyncResponseStream  # type: ignore[assignment]
openai_responses.ResponseStream = AIMLResponseStream  # type: ignore[assignment]
openai_responses.AsyncResponseStream = AIMLAsyncResponseStream  # type: ignore[assignment]

Responses = openai_responses.Responses
AsyncResponses = openai_responses.AsyncResponses
ResponseStream = openai_responses.ResponseStream
AsyncResponseStream = openai_responses.AsyncResponseStream

__all__ = [
    "Responses",
    "AsyncResponses",
    "ResponseStream",
    "AsyncResponseStream",
]
