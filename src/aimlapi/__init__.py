"""AI/ML API Python SDK.

Overlay on top of the official `openai` client that provides
an AIMLAPI-specific import path and default client.
"""

from __future__ import annotations

import os
import sys
import types as _types
from typing import Any, Mapping

import httpx
import openai as _openai
from openai import *  # noqa: F401, F403
from openai._base_client import DEFAULT_MAX_RETRIES, DEFAULT_TIMEOUT
from openai._client import Timeout

from ._client import (
    AIMLAPI,
    AIMLAPIWithRawResponse,
    AIMLAPIWithStreamedResponse,
    AsyncAIMLAPI,
    AsyncAIMLAPIWithRawResponse,
    AsyncAIMLAPIWithStreamedResponse,
    AsyncAzureAIMLAPI,
    AsyncAzureAIMLAPIWithRawResponse,
    AsyncAzureAIMLAPIWithStreamedResponse,
    AsyncClient,
    AzureAIMLAPI,
    AzureAIMLAPIWithRawResponse,
    AzureAIMLAPIWithStreamedResponse,
    Client,
)

AzureOpenAI = AzureAIMLAPI
AsyncAzureOpenAI = AsyncAzureAIMLAPI
AzureClient = AzureAIMLAPI
AsyncAzureClient = AsyncAzureAIMLAPI

_API_KEY_ENV_VARS = ("AIML_API_KEY", "AIMLAPI_API_KEY")
_BASE_URL_ENV_VARS = ("AIML_API_BASE", "AIMLAPI_API_BASE")


def _first_env(*names: str) -> str | None:
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return None


api_key: str | None = _first_env(*_API_KEY_ENV_VARS)
organization: str | None = None
project: str | None = None
webhook_secret: str | None = None
base_url: str | httpx.URL | None = _first_env(*_BASE_URL_ENV_VARS)
websocket_base_url: str | httpx.URL | None = None
timeout: float | Timeout | None = DEFAULT_TIMEOUT
max_retries: int = DEFAULT_MAX_RETRIES
default_headers: Mapping[str, str] | None = None
default_query: Mapping[str, object] | None = None
http_client: httpx.Client | None = None

_default_client: AIMLAPI | None = None


def _client_kwargs() -> dict[str, Any]:
    kwargs: dict[str, Any] = {}
    if api_key is not None:
        kwargs["api_key"] = api_key
    if organization is not None:
        kwargs["organization"] = organization
    if project is not None:
        kwargs["project"] = project
    if webhook_secret is not None:
        kwargs["webhook_secret"] = webhook_secret
    if base_url is not None:
        kwargs["base_url"] = base_url
    if websocket_base_url is not None:
        kwargs["websocket_base_url"] = websocket_base_url
    if timeout is not None:
        kwargs["timeout"] = timeout
    kwargs["max_retries"] = max_retries
    if default_headers is not None:
        kwargs["default_headers"] = default_headers
    if default_query is not None:
        kwargs["default_query"] = default_query
    if http_client is not None:
        kwargs["http_client"] = http_client
    return kwargs


def _reset_default_client() -> None:
    global _default_client
    _default_client = None


def _set_config_value(name: str, value: Any) -> None:
    globals()[name] = value
    _reset_default_client()


def _get_default_client() -> AIMLAPI:
    global _default_client
    if _default_client is None:
        _default_client = AIMLAPI(**_client_kwargs())
    return _default_client


_openai_all = getattr(_openai, "__all__", None)
if _openai_all is None:
    _openai_all = [name for name in dir(_openai) if not name.startswith("_")]

__all__ = list(
    dict.fromkeys(
        [
            *_openai_all,
            "AIMLAPI",
            "AsyncAIMLAPI",
            "AIMLAPIWithRawResponse",
            "AsyncAIMLAPIWithRawResponse",
            "AIMLAPIWithStreamedResponse",
            "AsyncAIMLAPIWithStreamedResponse",
            "Client",
            "AsyncClient",
            "AzureAIMLAPI",
            "AsyncAzureAIMLAPI",
            "AzureAIMLAPIWithRawResponse",
            "AsyncAzureAIMLAPIWithRawResponse",
            "AzureAIMLAPIWithStreamedResponse",
            "AsyncAzureAIMLAPIWithStreamedResponse",
            "AzureOpenAI",
            "AsyncAzureOpenAI",
            "AzureClient",
            "AsyncAzureClient",
            "api_key",
            "organization",
            "project",
            "webhook_secret",
            "base_url",
            "websocket_base_url",
            "timeout",
            "max_retries",
            "default_headers",
            "default_query",
            "http_client",
        ]
    )
)


def __dir__() -> list[str]:
    return sorted(set(__all__))


def __getattr__(name: str) -> Any:
    if hasattr(_openai, name):
        return getattr(_openai, name)

    client = _get_default_client()
    if hasattr(client, name):
        return getattr(client, name)

    raise AttributeError(f"module 'aimlapi' has no attribute {name!r}")


_RESOURCE_PROXY_NAMES = (
    "audio",
    "beta",
    "batches",
    "chat",
    "completions",
    "containers",
    "conversations",
    "embeddings",
    "evals",
    "files",
    "fine_tuning",
    "images",
    "models",
    "moderations",
    "realtime",
    "responses",
    "uploads",
    "vector_stores",
    "videos",
    "webhooks",
)

_CONFIG_ATTRS = {
    "api_key",
    "organization",
    "project",
    "webhook_secret",
    "base_url",
    "websocket_base_url",
    "timeout",
    "max_retries",
    "default_headers",
    "default_query",
    "http_client",
}


class _AIMLAPIModule(_types.ModuleType):
    def __setattr__(self, name: str, value: Any) -> None:  # type: ignore[override]
        if name in _CONFIG_ATTRS:
            _set_config_value(name, value)
        super().__setattr__(name, value)


_module = sys.modules[__name__]
if not isinstance(_module, _AIMLAPIModule):
    _module.__class__ = _AIMLAPIModule


class _ModuleResourceProxy:
    __slots__ = ("_attr",)

    def __init__(self, attr: str) -> None:
        self._attr = attr

    def __getattr__(self, name: str) -> Any:
        resource = getattr(_get_default_client(), self._attr)
        return getattr(resource, name)

    def __repr__(self) -> str:
        resource = getattr(_get_default_client(), self._attr)
        return repr(resource)

    def __dir__(self) -> list[str]:
        resource = getattr(_get_default_client(), self._attr)
        return sorted(set(dir(resource)))


for _resource_name in _RESOURCE_PROXY_NAMES:
    globals()[_resource_name] = _ModuleResourceProxy(_resource_name)
