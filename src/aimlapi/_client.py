from __future__ import annotations

import os
from collections.abc import MutableMapping, Sequence
from typing import Any

from typing_extensions import override

from openai._client import (
    OpenAI as _OpenAI,
    AsyncOpenAI as _AsyncOpenAI,
    OpenAIWithRawResponse as _OpenAIWithRawResponse,
    AsyncOpenAIWithRawResponse as _AsyncOpenAIWithRawResponse,
    OpenAIWithStreamedResponse as _OpenAIWithStreamedResponse,
    AsyncOpenAIWithStreamedResponse as _AsyncOpenAIWithStreamedResponse,
)
from openai._models import FinalRequestOptions
from openai.lib.azure import AzureOpenAI as _AzureOpenAI, AsyncAzureOpenAI as _AsyncAzureOpenAI

DEFAULT_BASE_URL = "https://api.aimlapi.com/v1"
_API_KEY_ENV_VARS = ("AIML_API_KEY", "AIMLAPI_API_KEY")
_BASE_URL_ENV_VARS = ("AIML_API_BASE", "AIMLAPI_API_BASE")


def _first_env(*names: str) -> str | None:
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return None


def _apply_default_client_options(kwargs: dict[str, Any]) -> None:
    if kwargs.get("api_key") is None:
        api_key = _first_env(*_API_KEY_ENV_VARS)
        if api_key is not None:
            kwargs["api_key"] = api_key

    if kwargs.get("base_url") is None:
        base_url = _first_env(*_BASE_URL_ENV_VARS) or DEFAULT_BASE_URL
        kwargs["base_url"] = base_url


def _scrub_schema_fields(value: object) -> None:
    if isinstance(value, MutableMapping):
        value.pop("title", None)
        value.pop("$defs", None)
        for child in value.values():
            _scrub_schema_fields(child)
        return

    if isinstance(value, list):
        for item in value:
            _scrub_schema_fields(item)


def _clean_tool_schemas(payload: object) -> None:
    if not isinstance(payload, MutableMapping):
        return

    tools = payload.get("tools")
    if not isinstance(tools, Sequence) or isinstance(tools, (str, bytes, bytearray)):
        return

    for tool in tools:
        if not isinstance(tool, MutableMapping):
            continue
        function = tool.get("function")
        if not isinstance(function, MutableMapping):
            continue
        function.pop("strict", None)

        parameters = function.get("parameters")
        if parameters is not None:
            _scrub_schema_fields(parameters)


def _prepare_tool_schemas(options: FinalRequestOptions) -> None:
    _clean_tool_schemas(options.json_data)


class _ToolSchemaCleanupMixin:
    """Shared cleanup hook for AIMLAPI clients."""

    @staticmethod
    def _cleanup_request(options: FinalRequestOptions) -> None:
        _prepare_tool_schemas(options)


class AIMLAPI(_ToolSchemaCleanupMixin, _OpenAI):
    """Synchronous client for the AIML API."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        _apply_default_client_options(kwargs)
        super().__init__(*args, **kwargs)

    @override
    def _build_request(self, options: FinalRequestOptions, *, retries_taken: int = 0):
        self._cleanup_request(options)
        return super()._build_request(options, retries_taken=retries_taken)


class AsyncAIMLAPI(_ToolSchemaCleanupMixin, _AsyncOpenAI):
    """Asynchronous client for the AIML API."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        _apply_default_client_options(kwargs)
        super().__init__(*args, **kwargs)

    @override
    def _build_request(self, options: FinalRequestOptions, *, retries_taken: int = 0):
        self._cleanup_request(options)
        return super()._build_request(options, retries_taken=retries_taken)


class AzureAIMLAPI(_ToolSchemaCleanupMixin, _AzureOpenAI):
    """Synchronous Azure client with AIMLAPI overrides."""

    @override
    def _build_request(self, options: FinalRequestOptions, *, retries_taken: int = 0):
        self._cleanup_request(options)
        return super()._build_request(options, retries_taken=retries_taken)


class AsyncAzureAIMLAPI(_ToolSchemaCleanupMixin, _AsyncAzureOpenAI):
    """Asynchronous Azure client with AIMLAPI overrides."""

    @override
    def _build_request(self, options: FinalRequestOptions, *, retries_taken: int = 0):
        self._cleanup_request(options)
        return super()._build_request(options, retries_taken=retries_taken)


class AIMLAPIWithRawResponse(_OpenAIWithRawResponse):
    _client: AIMLAPI

    def __init__(self, client: AIMLAPI) -> None:
        super().__init__(client)


class AsyncAIMLAPIWithRawResponse(_AsyncOpenAIWithRawResponse):
    _client: AsyncAIMLAPI

    def __init__(self, client: AsyncAIMLAPI) -> None:
        super().__init__(client)


class AIMLAPIWithStreamedResponse(_OpenAIWithStreamedResponse):
    _client: AIMLAPI

    def __init__(self, client: AIMLAPI) -> None:
        super().__init__(client)


class AsyncAIMLAPIWithStreamedResponse(_AsyncOpenAIWithStreamedResponse):
    _client: AsyncAIMLAPI

    def __init__(self, client: AsyncAIMLAPI) -> None:
        super().__init__(client)


class AzureAIMLAPIWithRawResponse(_OpenAIWithRawResponse):
    _client: AzureAIMLAPI

    def __init__(self, client: AzureAIMLAPI) -> None:
        super().__init__(client)


class AsyncAzureAIMLAPIWithRawResponse(_AsyncOpenAIWithRawResponse):
    _client: AsyncAzureAIMLAPI

    def __init__(self, client: AsyncAzureAIMLAPI) -> None:
        super().__init__(client)


class AzureAIMLAPIWithStreamedResponse(_OpenAIWithStreamedResponse):
    _client: AzureAIMLAPI

    def __init__(self, client: AzureAIMLAPI) -> None:
        super().__init__(client)


class AsyncAzureAIMLAPIWithStreamedResponse(_AsyncOpenAIWithStreamedResponse):
    _client: AsyncAzureAIMLAPI

    def __init__(self, client: AsyncAzureAIMLAPI) -> None:
        super().__init__(client)


Client = AIMLAPI
AsyncClient = AsyncAIMLAPI

# Backwards-compatible aliases.
OpenAI = AIMLAPI
AsyncOpenAI = AsyncAIMLAPI
AzureOpenAI = AzureAIMLAPI
AsyncAzureOpenAI = AsyncAzureAIMLAPI
