from __future__ import annotations

import base64
import gzip
import inspect
import json
import logging
from typing import Any, Iterable, Callable, Awaitable

import httpx

from openai._streaming import Stream, AsyncStream
from openai.resources.images import AsyncImages as _AsyncImages
from openai.resources.images import Images as _Images
from openai.types.image_gen_stream_event import ImageGenStreamEvent
from openai.types.images_response import ImagesResponse

logger = logging.getLogger(__name__)

__all__ = ["Images", "AsyncImages"]


def _maybe_decompress_body(body: bytes, response: httpx.Response) -> bytes:
    if response.headers.get("content-encoding", "").lower() == "gzip":
        try:
            # Decompress if gzipped
            return gzip.decompress(body)
        except Exception:
            logger.warning(
                "Failed to decompress gzipped response body; using raw bytes",
                exc_info=True,
            )
    return body


def _decode_stream_response(
    *,
    response: httpx.Response,
    process_data: Callable[..., ImagesResponse],
    response_format: str | None,
    http_client: httpx.Client,
    body: bytes | None = None,
) -> ImagesResponse:
    if body is None:
        body = b"".join(response.iter_bytes())
    body = _maybe_decompress_body(body, response)

    parsed = json.loads(body.decode("utf-8"))
    result = process_data(data=parsed, cast_to=ImagesResponse, response=response)

    return ensure_b64_json_images_response(
        result,
        response=response,
        response_format=response_format,
        http_client=http_client,
    )


async def _async_decode_stream_response(
    *,
    response: httpx.Response,
    process_data: Callable[..., Awaitable[ImagesResponse]] | Callable[..., ImagesResponse],
    response_format: str | None,
    http_client: httpx.AsyncClient,
    body: bytes | None = None,
) -> ImagesResponse:
    if body is None:
        body = b""
        async for chunk in response.aiter_bytes():
            body += chunk

    body = _maybe_decompress_body(body, response)

    parsed = json.loads(body.decode("utf-8"))
    result = process_data(data=parsed, cast_to=ImagesResponse, response=response)
    if inspect.isawaitable(result):
        result = await result

    return await async_ensure_b64_json_images_response(
        result,
        response=response,
        response_format=response_format,
        http_client=http_client,
    )


class _ImageStream(Stream[ImageGenStreamEvent]):
    def __init__(
        self,
        *,
        cast_to: type[ImageGenStreamEvent],
        response: httpx.Response,
        client: _Images,
        response_format: str | None,
    ) -> None:
        super().__init__(cast_to=cast_to, response=response, client=client)
        self._response_format = response_format
        self._http_client = client._client
        self._final_response: ImagesResponse | None = None
        self._body_chunks: list[bytes] = []

    def _iter_events(self):
        for sse in self._decoder.iter_bytes(self._iter_bytes_with_buffer()):
            yield sse

    def _iter_bytes_with_buffer(self):
        for chunk in self.response.iter_bytes():
            self._body_chunks.append(chunk)
            yield chunk

    def __iter__(self):
        for event in super().__iter__():
            yield self._maybe_enrich_stream_event(event)

    def get_final_response(self) -> ImagesResponse:
        if self._final_response is None:
            if self._body_chunks:
                self._final_response = _decode_stream_response(
                    response=self.response,
                    process_data=self._client._process_response_data,
                    response_format=self._response_format,
                    http_client=self._http_client,
                    body=b"".join(self._body_chunks),
                )
            else:
                self._final_response = _decode_stream_response(
                    response=self.response,
                    process_data=self._client._process_response_data,
                    response_format=self._response_format,
                    http_client=self._http_client,
                )

        return self._final_response

    def _maybe_enrich_stream_event(self, event: Any) -> Any:
        response_format = self._response_format or _extract_response_format(
            self.response.request
        )

        if response_format != "b64_json":
            return event

        if not hasattr(event, "b64_json"):
            return event

        if getattr(event, "b64_json", None):
            return event

        url = getattr(event, "url", None)
        if not url:
            # Try to reuse the enriched final response if available for single-image streams.
            try:
                final_response = self.get_final_response()
                if final_response and getattr(final_response, "data", None):
                    first_image = next(iter(_iter_images(final_response.data)), None)
                    if first_image and getattr(first_image, "b64_json", None):
                        event.b64_json = first_image.b64_json
            except Exception:
                logger.warning("Failed to populate stream event b64_json", exc_info=True)
            return event

        try:
            resp = self._http_client.get(url)
            resp.raise_for_status()
            image_bytes = resp.content

            if resp.headers.get("content-encoding", "").lower() == "gzip":
                try:
                    # Decompress if gzipped
                    image_bytes = gzip.decompress(image_bytes)
                except Exception:
                    logger.warning(
                        "Failed to decompress gzipped image content; using raw bytes",
                        exc_info=True,
                    )
            event.b64_json = base64.b64encode(image_bytes).decode()
        except Exception:
            logger.warning("Failed to enrich stream event b64_json", exc_info=True)

        return event


class _AsyncImageStream(AsyncStream[ImageGenStreamEvent]):
    def __init__(
        self,
        *,
        cast_to: type[ImageGenStreamEvent],
        response: httpx.Response,
        client: _AsyncImages,
        response_format: str | None,
    ) -> None:
        super().__init__(cast_to=cast_to, response=response, client=client)
        self._response_format = response_format
        self._http_client = client._client
        self._final_response: ImagesResponse | None = None
        self._body_chunks: list[bytes] = []

    async def _iter_events(self):
        async for sse in self._decoder.aiter_bytes(self._aiter_bytes_with_buffer()):
            yield sse

    async def _aiter_bytes_with_buffer(self):
        async for chunk in self.response.aiter_bytes():
            self._body_chunks.append(chunk)
            yield chunk

    async def __aiter__(self):
        async for event in super().__aiter__():
            yield await self._maybe_enrich_stream_event(event)

    async def get_final_response(self) -> ImagesResponse:
        if self._final_response is None:
            if self._body_chunks:
                self._final_response = await _async_decode_stream_response(
                    response=self.response,
                    process_data=self._client._process_response_data,
                    response_format=self._response_format,
                    http_client=self._http_client,
                    body=b"".join(self._body_chunks),
                )
            else:
                self._final_response = await _async_decode_stream_response(
                    response=self.response,
                    process_data=self._client._process_response_data,
                    response_format=self._response_format,
                    http_client=self._http_client,
                )

        return self._final_response

    async def _maybe_enrich_stream_event(self, event: Any) -> Any:
        response_format = self._response_format or _extract_response_format(
            self.response.request
        )

        if response_format != "b64_json":
            return event

        if not hasattr(event, "b64_json"):
            return event

        if getattr(event, "b64_json", None):
            return event

        url = getattr(event, "url", None)
        if not url:
            try:
                final_response = await self.get_final_response()
                if final_response and getattr(final_response, "data", None):
                    first_image = next(iter(_iter_images(final_response.data)), None)
                    if first_image and getattr(first_image, "b64_json", None):
                        event.b64_json = first_image.b64_json
            except Exception:
                logger.warning("Failed to populate async stream event b64_json", exc_info=True)
            return event

        try:
            resp = await self._http_client.get(url)
            resp.raise_for_status()
            image_bytes = resp.content

            if resp.headers.get("content-encoding", "").lower() == "gzip":
                try:
                    # Decompress if gzipped
                    image_bytes = gzip.decompress(image_bytes)
                except Exception:
                    logger.warning(
                        "Failed to decompress gzipped image content; using raw bytes",
                        exc_info=True,
                    )
            event.b64_json = base64.b64encode(image_bytes).decode()
        except Exception:
            logger.warning("Failed to enrich async stream event b64_json", exc_info=True)

        return event


class Images(_Images):
    def generate(self, *args: Any, **kwargs: Any):
        response_format = kwargs.get("response_format")
        result = super().generate(*args, **kwargs)

        if isinstance(result, Stream):
            return _ImageStream(
                cast_to=result._cast_to,
                response=result.response,
                client=result._client,
                response_format=response_format if isinstance(response_format, str) else None,
            )

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

        if isinstance(result, AsyncStream):
            return _AsyncImageStream(
                cast_to=result._cast_to,
                response=result.response,
                client=result._client,
                response_format=response_format if isinstance(response_format, str) else None,
            )

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

                if resp.headers.get("content-encoding", "").lower() == "gzip":
                    try:
                        # Decompress if gzipped
                        image_bytes = gzip.decompress(image_bytes)
                    except Exception:
                        logger.warning(
                            "Failed to decompress gzipped image content; using raw bytes",
                            exc_info=True,
                        )
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

                if resp.headers.get("content-encoding", "").lower() == "gzip":
                    try:
                        # Decompress if gzipped
                        image_bytes = gzip.decompress(image_bytes)
                    except Exception:
                        logger.warning(
                            "Failed to decompress gzipped image content; using raw bytes",
                            exc_info=True,
                        )
            except Exception:
                logger.warning("Failed to download image content for base64 enrichment", exc_info=True)
                continue

            try:
                image.b64_json = base64.b64encode(image_bytes).decode()
            except Exception:
                logger.warning("Failed to base64-encode downloaded image content", exc_info=True)

    return result
