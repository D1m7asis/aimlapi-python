from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any, Union, overload

from typing_extensions import Literal

from openai._streaming import AsyncStream, Stream
from openai.resources.chat.completions.completions import (
    AsyncCompletions as _AsyncCompletions,
    Completions as _Completions,
    AsyncCompletionsWithRawResponse as AsyncCompletionsWithRawResponse,
    AsyncCompletionsWithStreamingResponse as AsyncCompletionsWithStreamingResponse,
    CompletionsWithRawResponse as CompletionsWithRawResponse,
    CompletionsWithStreamingResponse as CompletionsWithStreamingResponse,
)
from openai.types.chat.chat_completion import ChatCompletion
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam

MessageDict = Mapping[str, object]
MessageParam = Union[ChatCompletionMessageParam, MessageDict]


class Completions(_Completions):
    """Override that accepts plain ``dict`` message payloads."""

    @overload
    def create(
        self,
        *,
        messages: Iterable[MessageParam],
        stream: Literal[True],
        **kwargs: Any,
    ) -> Stream[ChatCompletionChunk]:
        ...

    @overload
    def create(
        self,
        *,
        messages: Iterable[MessageParam],
        stream: Literal[False] | None = ...,
        **kwargs: Any,
    ) -> ChatCompletion:
        ...

    def create(
        self,
        *,
        messages: Iterable[MessageParam],
        stream: bool | None = None,
        **kwargs: Any,
    ) -> ChatCompletion | Stream[ChatCompletionChunk]:
        return super().create(messages=messages, stream=stream, **kwargs)


class AsyncCompletions(_AsyncCompletions):
    """Async override that accepts plain ``dict`` message payloads."""

    @overload
    async def create(
        self,
        *,
        messages: Iterable[MessageParam],
        stream: Literal[True],
        **kwargs: Any,
    ) -> AsyncStream[ChatCompletionChunk]:
        ...

    @overload
    async def create(
        self,
        *,
        messages: Iterable[MessageParam],
        stream: Literal[False] | None = ...,
        **kwargs: Any,
    ) -> ChatCompletion:
        ...

    async def create(
        self,
        *,
        messages: Iterable[MessageParam],
        stream: bool | None = None,
        **kwargs: Any,
    ) -> ChatCompletion | AsyncStream[ChatCompletionChunk]:
        return await super().create(messages=messages, stream=stream, **kwargs)


__all__ = [
    "Completions",
    "AsyncCompletions",
    "CompletionsWithRawResponse",
    "AsyncCompletionsWithRawResponse",
    "CompletionsWithStreamingResponse",
    "AsyncCompletionsWithStreamingResponse",
]
