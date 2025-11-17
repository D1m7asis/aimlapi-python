"""AI/ML API Python SDK.

This package re-exports the functionality implemented in :mod:`openai` while
providing a provider-specific import path for the AI/ML API service.
"""

from __future__ import annotations

from typing import Any

import openai as _openai
from openai import *  # noqa: F401,F403

_default_client: _openai.AIMLAPI | None = None


def _get_default_client() -> _openai.AIMLAPI:
    global _default_client
    if _default_client is None:
        _default_client = _openai.AIMLAPI()
    return _default_client


_openai_all = getattr(_openai, "__all__", None)
if _openai_all is None:
    _openai_all = [name for name in dir(_openai) if not name.startswith("_")]

__all__ = list(dict.fromkeys([
    *_openai_all,
    "AIMLAPI",
    "AsyncAIMLAPI",
    "OpenAI",
    "AsyncOpenAI",
]))


def __dir__() -> list[str]:
    return sorted(set(__all__))


def __getattr__(name: str) -> Any:
    if hasattr(_openai, name):
        return getattr(_openai, name)

    client = _get_default_client()
    if hasattr(client, name):
        return getattr(client, name)

    raise AttributeError(f"module 'aimlapi' has no attribute {name!r}")
