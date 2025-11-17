from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any, Dict, List, Optional, Union, overload

import httpx
from typing_extensions import Literal

from openai._streaming import AsyncStream, Stream
from openai._types import (
    Body,
    Headers,
    NotGiven,
    Omit,
    Query,
    SequenceNotStr,
    omit,
    not_given,
)
from openai.resources.chat.completions.completions import (
    AsyncCompletions as _AsyncCompletions,
    Completions as _Completions,
    AsyncCompletionsWithRawResponse as AsyncCompletionsWithRawResponse,
    AsyncCompletionsWithStreamingResponse as AsyncCompletionsWithStreamingResponse,
    CompletionsWithRawResponse as CompletionsWithRawResponse,
    CompletionsWithStreamingResponse as CompletionsWithStreamingResponse,
)
from openai.lib._parsing import ResponseFormatT
from openai.lib.streaming.chat import (
    AsyncChatCompletionStreamManager,
    ChatCompletionStreamManager,
)
from openai.types.chat import completion_create_params
from openai.types.chat.chat_completion import ChatCompletion
from openai.types.chat.chat_completion_audio_param import ChatCompletionAudioParam
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from openai.types.chat.chat_completion_prediction_content_param import (
    ChatCompletionPredictionContentParam,
)
from openai.types.chat.chat_completion_stream_options_param import (
    ChatCompletionStreamOptionsParam,
)
from openai.types.chat.chat_completion_tool_choice_option_param import (
    ChatCompletionToolChoiceOptionParam,
)
from openai.types.chat.chat_completion_tool_union_param import ChatCompletionToolUnionParam
from openai.types.chat.parsed_chat_completion import ParsedChatCompletion
from openai.types.shared.chat_model import ChatModel
from openai.types.shared.reasoning_effort import ReasoningEffort
from openai.types.shared_params.metadata import Metadata

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
        stream_value = False if stream is None else stream
        return super().create(messages=messages, stream=stream_value, **kwargs)

    def parse(
        self,
        *,
        messages: Iterable[MessageParam],
        model: Union[str, ChatModel],
        audio: ChatCompletionAudioParam | Omit = omit,
        response_format: type[ResponseFormatT] | Omit = omit,
        frequency_penalty: Optional[float] | Omit = omit,
        function_call: completion_create_params.FunctionCall | Omit = omit,
        functions: Iterable[completion_create_params.Function] | Omit = omit,
        logit_bias: Optional[Dict[str, int]] | Omit = omit,
        logprobs: Optional[bool] | Omit = omit,
        max_completion_tokens: Optional[int] | Omit = omit,
        max_tokens: Optional[int] | Omit = omit,
        metadata: Optional[Metadata] | Omit = omit,
        modalities: Optional[List[Literal["text", "audio"]]] | Omit = omit,
        n: Optional[int] | Omit = omit,
        parallel_tool_calls: bool | Omit = omit,
        prediction: Optional[ChatCompletionPredictionContentParam] | Omit = omit,
        presence_penalty: Optional[float] | Omit = omit,
        prompt_cache_key: str | Omit = omit,
        reasoning_effort: Optional[ReasoningEffort] | Omit = omit,
        safety_identifier: str | Omit = omit,
        seed: Optional[int] | Omit = omit,
        service_tier: Optional[Literal["auto", "default", "flex", "scale", "priority"]] | Omit = omit,
        stop: Union[Optional[str], SequenceNotStr[str], None] | Omit = omit,
        store: Optional[bool] | Omit = omit,
        stream_options: Optional[ChatCompletionStreamOptionsParam] | Omit = omit,
        temperature: Optional[float] | Omit = omit,
        tool_choice: ChatCompletionToolChoiceOptionParam | Omit = omit,
        tools: Iterable[ChatCompletionToolUnionParam] | Omit = omit,
        top_logprobs: Optional[int] | Omit = omit,
        top_p: Optional[float] | Omit = omit,
        user: str | Omit = omit,
        verbosity: Optional[Literal["low", "medium", "high"]] | Omit = omit,
        web_search_options: completion_create_params.WebSearchOptions | Omit = omit,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ParsedChatCompletion[ResponseFormatT]:
        return super().parse(
            messages=messages,
            model=model,
            audio=audio,
            response_format=response_format,
            frequency_penalty=frequency_penalty,
            function_call=function_call,
            functions=functions,
            logit_bias=logit_bias,
            logprobs=logprobs,
            max_completion_tokens=max_completion_tokens,
            max_tokens=max_tokens,
            metadata=metadata,
            modalities=modalities,
            n=n,
            parallel_tool_calls=parallel_tool_calls,
            prediction=prediction,
            presence_penalty=presence_penalty,
            prompt_cache_key=prompt_cache_key,
            reasoning_effort=reasoning_effort,
            safety_identifier=safety_identifier,
            seed=seed,
            service_tier=service_tier,
            stop=stop,
            store=store,
            stream_options=stream_options,
            temperature=temperature,
            tool_choice=tool_choice,
            tools=tools,
            top_logprobs=top_logprobs,
            top_p=top_p,
            user=user,
            verbosity=verbosity,
            web_search_options=web_search_options,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        )

    def stream(
        self,
        *,
        messages: Iterable[MessageParam],
        model: Union[str, ChatModel],
        audio: Optional[ChatCompletionAudioParam] | Omit = omit,
        response_format: completion_create_params.ResponseFormat | type[ResponseFormatT] | Omit = omit,
        frequency_penalty: Optional[float] | Omit = omit,
        function_call: completion_create_params.FunctionCall | Omit = omit,
        functions: Iterable[completion_create_params.Function] | Omit = omit,
        logit_bias: Optional[Dict[str, int]] | Omit = omit,
        logprobs: Optional[bool] | Omit = omit,
        max_completion_tokens: Optional[int] | Omit = omit,
        max_tokens: Optional[int] | Omit = omit,
        metadata: Optional[Metadata] | Omit = omit,
        modalities: Optional[List[Literal["text", "audio"]]] | Omit = omit,
        n: Optional[int] | Omit = omit,
        parallel_tool_calls: bool | Omit = omit,
        prediction: Optional[ChatCompletionPredictionContentParam] | Omit = omit,
        presence_penalty: Optional[float] | Omit = omit,
        prompt_cache_key: str | Omit = omit,
        reasoning_effort: Optional[ReasoningEffort] | Omit = omit,
        safety_identifier: str | Omit = omit,
        seed: Optional[int] | Omit = omit,
        service_tier: Optional[Literal["auto", "default", "flex", "scale", "priority"]] | Omit = omit,
        stop: Union[Optional[str], SequenceNotStr[str], None] | Omit = omit,
        store: Optional[bool] | Omit = omit,
        stream_options: Optional[ChatCompletionStreamOptionsParam] | Omit = omit,
        temperature: Optional[float] | Omit = omit,
        tool_choice: ChatCompletionToolChoiceOptionParam | Omit = omit,
        tools: Iterable[ChatCompletionToolUnionParam] | Omit = omit,
        top_logprobs: Optional[int] | Omit = omit,
        top_p: Optional[float] | Omit = omit,
        user: str | Omit = omit,
        verbosity: Optional[Literal["low", "medium", "high"]] | Omit = omit,
        web_search_options: completion_create_params.WebSearchOptions | Omit = omit,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ChatCompletionStreamManager[ResponseFormatT]:
        return super().stream(
            messages=messages,
            model=model,
            audio=audio,
            response_format=response_format,
            frequency_penalty=frequency_penalty,
            function_call=function_call,
            functions=functions,
            logit_bias=logit_bias,
            logprobs=logprobs,
            max_completion_tokens=max_completion_tokens,
            max_tokens=max_tokens,
            metadata=metadata,
            modalities=modalities,
            n=n,
            parallel_tool_calls=parallel_tool_calls,
            prediction=prediction,
            presence_penalty=presence_penalty,
            prompt_cache_key=prompt_cache_key,
            reasoning_effort=reasoning_effort,
            safety_identifier=safety_identifier,
            seed=seed,
            service_tier=service_tier,
            stop=stop,
            store=store,
            stream_options=stream_options,
            temperature=temperature,
            tool_choice=tool_choice,
            tools=tools,
            top_logprobs=top_logprobs,
            top_p=top_p,
            user=user,
            verbosity=verbosity,
            web_search_options=web_search_options,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        )


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
        stream_value = False if stream is None else stream
        return await super().create(messages=messages, stream=stream_value, **kwargs)

    async def parse(
        self,
        *,
        messages: Iterable[MessageParam],
        model: Union[str, ChatModel],
        audio: ChatCompletionAudioParam | Omit = omit,
        response_format: type[ResponseFormatT] | Omit = omit,
        frequency_penalty: Optional[float] | Omit = omit,
        function_call: completion_create_params.FunctionCall | Omit = omit,
        functions: Iterable[completion_create_params.Function] | Omit = omit,
        logit_bias: Optional[Dict[str, int]] | Omit = omit,
        logprobs: Optional[bool] | Omit = omit,
        max_completion_tokens: Optional[int] | Omit = omit,
        max_tokens: Optional[int] | Omit = omit,
        metadata: Optional[Metadata] | Omit = omit,
        modalities: Optional[List[Literal["text", "audio"]]] | Omit = omit,
        n: Optional[int] | Omit = omit,
        parallel_tool_calls: bool | Omit = omit,
        prediction: Optional[ChatCompletionPredictionContentParam] | Omit = omit,
        presence_penalty: Optional[float] | Omit = omit,
        prompt_cache_key: str | Omit = omit,
        reasoning_effort: Optional[ReasoningEffort] | Omit = omit,
        safety_identifier: str | Omit = omit,
        seed: Optional[int] | Omit = omit,
        service_tier: Optional[Literal["auto", "default", "flex", "scale", "priority"]] | Omit = omit,
        stop: Union[Optional[str], SequenceNotStr[str], None] | Omit = omit,
        store: Optional[bool] | Omit = omit,
        stream_options: Optional[ChatCompletionStreamOptionsParam] | Omit = omit,
        temperature: Optional[float] | Omit = omit,
        tool_choice: ChatCompletionToolChoiceOptionParam | Omit = omit,
        tools: Iterable[ChatCompletionToolUnionParam] | Omit = omit,
        top_logprobs: Optional[int] | Omit = omit,
        top_p: Optional[float] | Omit = omit,
        user: str | Omit = omit,
        verbosity: Optional[Literal["low", "medium", "high"]] | Omit = omit,
        web_search_options: completion_create_params.WebSearchOptions | Omit = omit,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ParsedChatCompletion[ResponseFormatT]:
        return await super().parse(
            messages=messages,
            model=model,
            audio=audio,
            response_format=response_format,
            frequency_penalty=frequency_penalty,
            function_call=function_call,
            functions=functions,
            logit_bias=logit_bias,
            logprobs=logprobs,
            max_completion_tokens=max_completion_tokens,
            max_tokens=max_tokens,
            metadata=metadata,
            modalities=modalities,
            n=n,
            parallel_tool_calls=parallel_tool_calls,
            prediction=prediction,
            presence_penalty=presence_penalty,
            prompt_cache_key=prompt_cache_key,
            reasoning_effort=reasoning_effort,
            safety_identifier=safety_identifier,
            seed=seed,
            service_tier=service_tier,
            stop=stop,
            store=store,
            stream_options=stream_options,
            temperature=temperature,
            tool_choice=tool_choice,
            tools=tools,
            top_logprobs=top_logprobs,
            top_p=top_p,
            user=user,
            verbosity=verbosity,
            web_search_options=web_search_options,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        )

    def stream(
        self,
        *,
        messages: Iterable[MessageParam],
        model: Union[str, ChatModel],
        audio: Optional[ChatCompletionAudioParam] | Omit = omit,
        response_format: completion_create_params.ResponseFormat | type[ResponseFormatT] | Omit = omit,
        frequency_penalty: Optional[float] | Omit = omit,
        function_call: completion_create_params.FunctionCall | Omit = omit,
        functions: Iterable[completion_create_params.Function] | Omit = omit,
        logit_bias: Optional[Dict[str, int]] | Omit = omit,
        logprobs: Optional[bool] | Omit = omit,
        max_completion_tokens: Optional[int] | Omit = omit,
        max_tokens: Optional[int] | Omit = omit,
        metadata: Optional[Metadata] | Omit = omit,
        modalities: Optional[List[Literal["text", "audio"]]] | Omit = omit,
        n: Optional[int] | Omit = omit,
        parallel_tool_calls: bool | Omit = omit,
        prediction: Optional[ChatCompletionPredictionContentParam] | Omit = omit,
        presence_penalty: Optional[float] | Omit = omit,
        prompt_cache_key: str | Omit = omit,
        reasoning_effort: Optional[ReasoningEffort] | Omit = omit,
        safety_identifier: str | Omit = omit,
        seed: Optional[int] | Omit = omit,
        service_tier: Optional[Literal["auto", "default", "flex", "scale", "priority"]] | Omit = omit,
        stop: Union[Optional[str], SequenceNotStr[str], None] | Omit = omit,
        store: Optional[bool] | Omit = omit,
        stream_options: Optional[ChatCompletionStreamOptionsParam] | Omit = omit,
        temperature: Optional[float] | Omit = omit,
        tool_choice: ChatCompletionToolChoiceOptionParam | Omit = omit,
        tools: Iterable[ChatCompletionToolUnionParam] | Omit = omit,
        top_logprobs: Optional[int] | Omit = omit,
        top_p: Optional[float] | Omit = omit,
        user: str | Omit = omit,
        verbosity: Optional[Literal["low", "medium", "high"]] | Omit = omit,
        web_search_options: completion_create_params.WebSearchOptions | Omit = omit,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncChatCompletionStreamManager[ResponseFormatT]:
        return super().stream(
            messages=messages,
            model=model,
            audio=audio,
            response_format=response_format,
            frequency_penalty=frequency_penalty,
            function_call=function_call,
            functions=functions,
            logit_bias=logit_bias,
            logprobs=logprobs,
            max_completion_tokens=max_completion_tokens,
            max_tokens=max_tokens,
            metadata=metadata,
            modalities=modalities,
            n=n,
            parallel_tool_calls=parallel_tool_calls,
            prediction=prediction,
            presence_penalty=presence_penalty,
            prompt_cache_key=prompt_cache_key,
            reasoning_effort=reasoning_effort,
            safety_identifier=safety_identifier,
            seed=seed,
            service_tier=service_tier,
            stop=stop,
            store=store,
            stream_options=stream_options,
            temperature=temperature,
            tool_choice=tool_choice,
            tools=tools,
            top_logprobs=top_logprobs,
            top_p=top_p,
            user=user,
            verbosity=verbosity,
            web_search_options=web_search_options,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        )


__all__ = [
    "Completions",
    "AsyncCompletions",
    "CompletionsWithRawResponse",
    "AsyncCompletionsWithRawResponse",
    "CompletionsWithStreamingResponse",
    "AsyncCompletionsWithStreamingResponse",
]
