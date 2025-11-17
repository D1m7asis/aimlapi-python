from __future__ import annotations

from openai._compat import cached_property
from openai._resource import AsyncAPIResource, SyncAPIResource

from .completions.completions import (
    AsyncCompletions,
    Completions,
    AsyncCompletionsWithRawResponse,
    CompletionsWithRawResponse,
    AsyncCompletionsWithStreamingResponse,
    CompletionsWithStreamingResponse,
)

__all__ = [
    "Chat",
    "AsyncChat",
    "ChatWithRawResponse",
    "AsyncChatWithRawResponse",
    "ChatWithStreamingResponse",
    "AsyncChatWithStreamingResponse",
]


class Chat(SyncAPIResource):
    @cached_property
    def completions(self) -> Completions:
        return Completions(self._client)

    @cached_property
    def with_raw_response(self) -> ChatWithRawResponse:
        return ChatWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ChatWithStreamingResponse:
        return ChatWithStreamingResponse(self)


class AsyncChat(AsyncAPIResource):
    @cached_property
    def completions(self) -> AsyncCompletions:
        return AsyncCompletions(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncChatWithRawResponse:
        return AsyncChatWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncChatWithStreamingResponse:
        return AsyncChatWithStreamingResponse(self)


class ChatWithRawResponse:
    def __init__(self, chat: Chat) -> None:
        self._chat = chat

    @cached_property
    def completions(self) -> CompletionsWithRawResponse:
        return CompletionsWithRawResponse(self._chat.completions)


class AsyncChatWithRawResponse:
    def __init__(self, chat: AsyncChat) -> None:
        self._chat = chat

    @cached_property
    def completions(self) -> AsyncCompletionsWithRawResponse:
        return AsyncCompletionsWithRawResponse(self._chat.completions)


class ChatWithStreamingResponse:
    def __init__(self, chat: Chat) -> None:
        self._chat = chat

    @cached_property
    def completions(self) -> CompletionsWithStreamingResponse:
        return CompletionsWithStreamingResponse(self._chat.completions)


class AsyncChatWithStreamingResponse:
    def __init__(self, chat: AsyncChat) -> None:
        self._chat = chat

    @cached_property
    def completions(self) -> AsyncCompletionsWithStreamingResponse:
        return AsyncCompletionsWithStreamingResponse(self._chat.completions)
