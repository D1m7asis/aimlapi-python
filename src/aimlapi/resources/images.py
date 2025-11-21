from __future__ import annotations

import base64
import gzip
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
        elif isinstance(result, Stream):
            result = prepare_image_stream(
                result,
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
        elif isinstance(result, AsyncStream):
            result = prepare_async_image_stream(
                result,
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


def _decompress_if_needed(body: bytes, headers: dict[str, str] | None) -> bytes:
    if not headers:
        return body

    if headers.get("content-encoding", "").lower() != "gzip":
        return body

    try:
        # Decompress if gzipped
        return gzip.decompress(body)
    except Exception:
        logger.warning("Failed to decompress gzipped payload; using raw bytes", exc_info=True)
        return body


def _decode_json_body(body: bytes) -> dict[str, Any]:
    try:
        return json.loads(body.decode("utf-8"))
    except Exception:
        logger.warning("Failed to decode JSON payload from streamed image response", exc_info=True)
        raise


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


def _prepare_stream_response(stream: Stream) -> None:
    body_chunks: list[bytes] = []

    def iter_and_buffer() -> Iterable[bytes]:
        try:
            for chunk in stream.response.iter_bytes(decode_content=True):
                body_chunks.append(chunk)
                yield chunk
        except Exception:
            logger.warning("Failed to iterate streamed image response", exc_info=True)

    try:
        stream.response.stream = iter_and_buffer()
        stream._aiml_body_buffer = body_chunks  # type: ignore[attr-defined]
    except Exception:
        logger.warning("Failed to prepare streamed response for decompression", exc_info=True)


def _build_final_images_response(
    *,
    stream: Stream,
    response_format: str | None,
    http_client: httpx.Client,
) -> ImagesResponse:
    response = stream.response
    buffered = getattr(stream, "_aiml_body_buffer", None)

    if buffered:
        body = b"".join(buffered)
    else:
        try:
            body = response.read()
        except Exception:
            logger.warning(
                "Failed to read streamed image response; falling back to iterating bytes", exc_info=True
            )
            body = b"".join(response.iter_bytes(decode_content=True))

    body = _decompress_if_needed(body, dict(response.headers))
    parsed = _decode_json_body(body)
    result = ImagesResponse.model_validate(parsed)

    return ensure_b64_json_images_response(
        result,
        response=response,
        response_format=response_format,
        http_client=http_client,
    )


def prepare_image_stream(
    stream: Stream,
    *,
    response_format: str | None,
    http_client: httpx.Client,
) -> Stream:
    _prepare_stream_response(stream)

    def get_final_response() -> ImagesResponse:
        return _build_final_images_response(
            stream=stream,
            response_format=response_format,
            http_client=http_client,
        )

    stream.get_final_response = get_final_response  # type: ignore[attr-defined]
    return stream


def _prepare_async_stream_response(stream: AsyncStream) -> None:
    body_chunks: list[bytes] = []

    async def aiter_and_buffer():
        try:
            async for chunk in stream.response.aiter_bytes(decode_content=True):
                body_chunks.append(chunk)
                yield chunk
        except Exception:
            logger.warning("Failed to iterate async streamed image response", exc_info=True)

    try:
        stream.response.stream = aiter_and_buffer()
        stream._aiml_body_buffer = body_chunks  # type: ignore[attr-defined]
    except Exception:
        logger.warning("Failed to prepare async streamed response for decompression", exc_info=True)


async def _build_final_async_images_response(
    *,
    stream: AsyncStream,
    response_format: str | None,
    http_client: httpx.AsyncClient,
) -> ImagesResponse:
    response = stream.response
    buffered = getattr(stream, "_aiml_body_buffer", None)

    if buffered:
        body = b"".join(buffered)
    else:
        try:
            body = await response.aread()
        except Exception:
            logger.warning(
                "Failed to read async streamed image response; falling back to iterating bytes",
                exc_info=True,
            )
            body = b""
            async for chunk in response.aiter_bytes(decode_content=True):
                body += chunk

    body = _decompress_if_needed(body, dict(response.headers))
    parsed = _decode_json_body(body)
    result = ImagesResponse.model_validate(parsed)

    return await async_ensure_b64_json_images_response(
        result,
        response=response,
        response_format=response_format,
        http_client=http_client,
    )


def prepare_async_image_stream(
    stream: AsyncStream,
    *,
    response_format: str | None,
    http_client: httpx.AsyncClient,
) -> AsyncStream:
    _prepare_async_stream_response(stream)

    async def get_final_response() -> ImagesResponse:
        return await _build_final_async_images_response(
            stream=stream,
            response_format=response_format,
            http_client=http_client,
        )

    stream.get_final_response = get_final_response  # type: ignore[attr-defined]
    return stream
