"""AI/ML API Python SDK.

Overlay on top of the official `openai` client that provides
an AIMLAPI-specific import path and default client.
"""

from __future__ import annotations

from typing import Any

import openai as _openai
from openai import *  # noqa: F401, F403

from ._client import (
    AIMLAPI,
    AsyncAIMLAPI,
    Client,
    AsyncClient,
    AIMLAPIWithRawResponse,
    AsyncAIMLAPIWithRawResponse,
    AIMLAPIWithStreamedResponse,
    AsyncAIMLAPIWithStreamedResponse,
    AzureAIMLAPI,
    AsyncAzureAIMLAPI,
    AzureAIMLAPIWithRawResponse,
    AsyncAzureAIMLAPIWithRawResponse,
    AzureAIMLAPIWithStreamedResponse,
    AsyncAzureAIMLAPIWithStreamedResponse,
)

AzureOpenAI = AzureAIMLAPI
AsyncAzureOpenAI = AsyncAzureAIMLAPI
AzureClient = AzureAIMLAPI
AsyncAzureClient = AsyncAzureAIMLAPI

_default_client: AIMLAPI | None = None


def _get_default_client() -> AIMLAPI:
    global _default_client
    if _default_client is None:
        _default_client = AIMLAPI()
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
