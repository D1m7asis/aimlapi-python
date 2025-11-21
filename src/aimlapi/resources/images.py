from __future__ import annotations

import base64
import json
import logging
from typing import Any, Iterable

import httpx

from openai._streaming import Stream, AsyncStream
from openai.resources.images import AsyncImages as _AsyncImages
from openai.resources.images import Images as _Images
from openai.types.image_gen_stream_event import ImageGenStreamEvent
from openai.types.images_response import ImagesResponse

logger = logging.getLogger(__name__)

__all__ = ["Images", "AsyncImages"]


class Images(_Images):
    def generate(self, *args: Any, **kwargs: Any):
        response_format = kwargs.get("response_format")
        result = super().generate(*args, **kwargs)

        if isinstance(result, ImagesResponse):
            result = ensure_b64_json_images_response(
                result,
                response=None,
                response_format=response_format if isinstance(response_format, str) else None,
                http_client=self._client._client,
            )

        return result


class AsyncImages(_AsyncImages):
    async def generate(
        self, *args: Any, **kwargs: Any
    ) -> ImagesResponse | AsyncStream[ImageGenStreamEvent] | Stream[ImageGenStreamEvent]:
        response_format = kwargs.get("response_format")
        result = await super().generate(*args, **kwargs)

        if isinstance(result, ImagesResponse):
            result = await async_ensure_b64_json_images_response(
                result,
                response=None,
                response_format=response_format if isinstance(response_format, str) else None,
                http_client=self._client._client,
            )

        return result


def _extract_response_format(request: httpx.Request | None) -> str | None:
    if request is None:
        return None

    if request.url.path.rstrip("/") != "/images/generations":
        return None

    try:
        if request.content:
            payload = json.loads(request.content)
            if isinstance(payload, dict):
                response_format = payload.get("response_format")
                if isinstance(response_format, str):
                    return response_format
    except Exception:
        return None

    return None


def _iter_images(data: Iterable[Any] | None) -> Iterable[Any]:
    return data or []


def ensure_b64_json_images_response(
    result: Any,
    *,
    response: httpx.Response | None,
    response_format: str | None = None,
    http_client: httpx.Client,
):
    if not isinstance(result, ImagesResponse):
        return result

    if not result.data:
        return result

    response_format = response_format or _extract_response_format(response.request if response else None)

    if response_format != "b64_json":
        return result

    for image in _iter_images(result.data):
        if getattr(image, "b64_json", None) is None:
            url = getattr(image, "url", None)
            if not url:
                continue

            try:
                resp = http_client.get(url)
                resp.raise_for_status()
                image_bytes = resp.content
            except Exception:
                logger.warning("Failed to download image content for base64 enrichment", exc_info=True)
                continue

            try:
                image.b64_json = base64.b64encode(image_bytes).decode()
            except Exception:
                logger.warning("Failed to base64-encode downloaded image content", exc_info=True)

    return result


async def async_ensure_b64_json_images_response(
    result: Any,
    *,
    response: httpx.Response | None,
    response_format: str | None = None,
    http_client: httpx.AsyncClient,
):
    if not isinstance(result, ImagesResponse):
        return result

    if not result.data:
        return result

    response_format = response_format or _extract_response_format(response.request if response else None)

    if response_format != "b64_json":
        return result

    for image in _iter_images(result.data):
        if getattr(image, "b64_json", None) is None:
            url = getattr(image, "url", None)
            if not url:
                continue

            try:
                resp = await http_client.get(url)
                resp.raise_for_status()
                image_bytes = resp.content
            except Exception:
                logger.warning("Failed to download image content for base64 enrichment", exc_info=True)
                continue

            try:
                image.b64_json = base64.b64encode(image_bytes).decode()
            except Exception:
                logger.warning("Failed to base64-encode downloaded image content", exc_info=True)

    return result
