from __future__ import annotations

from typing import Any, Callable, Dict, Mapping

from openai._base_client import make_request_options
from openai._types import Body, Headers, NotGiven, Query, Timeout, not_given
from openai.resources.videos import (
    AsyncVideos as OpenAIAsyncVideos,
    AsyncVideosWithRawResponse,
    AsyncVideosWithStreamingResponse,
    Videos as OpenAIVideos,
    VideosWithRawResponse,
    VideosWithStreamingResponse,
)

from .audio._polling import async_poll_job, poll_job

__all__ = [
    "Videos",
    "AsyncVideos",
    "VideosWithRawResponse",
    "AsyncVideosWithRawResponse",
    "VideosWithStreamingResponse",
    "AsyncVideosWithStreamingResponse",
]

_VIDEO_GENERATION_CREATE_PATH = "/v2/video/generations"
_VIDEO_GENERATION_STATUS_PATH = "/v2/video/generations?generation_id={generation_id}"
_VIDEO_PENDING_STATUSES = frozenset({"queued", "generating"})
_DEFAULT_POLL_INTERVAL = 10.0
_DEFAULT_POLL_TIMEOUT = 600.0


def _add_if_not_none(payload: Dict[str, Any], key: str, value: object | None) -> None:
    if value is not None:
        payload[key] = value


def _extract_generation_id(payload: Mapping[str, Any]) -> str | None:
    generation_id = payload.get("generation_id")
    if isinstance(generation_id, str):
        return generation_id

    id_value = payload.get("id")
    if isinstance(id_value, str):
        return id_value

    return None


def _coerce_mapping(value: object, *, context: str) -> Dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    raise TypeError(f"Unexpected response payload from {context}")


def _video_api_url(base_url: Any, path: str) -> str:
    normalized_path = path if path.startswith("/") else f"/{path}"
    normalized_base = base_url.copy_with(raw_path=b"/")
    base = str(normalized_base).rstrip("/")
    return f"{base}{normalized_path}"


class Videos(OpenAIVideos):
    """AIMLAPI specific video helpers."""

    def generate_with_polling(
        self,
        *,
        model: str,
        prompt: str,
        aspect_ratio: str | None = None,
        duration: int | None = None,
        negative_prompt: str | None = None,
        seed: int | None = None,
        enhance_prompt: bool | None = None,
        poll_interval: float = _DEFAULT_POLL_INTERVAL,
        poll_timeout: float | None = _DEFAULT_POLL_TIMEOUT,
        status_callback: Callable[[Mapping[str, Any]], None] | None = None,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
    ) -> Dict[str, Any]:
        """Create a video generation job and poll until it finishes."""

        payload: Dict[str, Any] = {
            "model": model,
            "prompt": prompt,
        }
        _add_if_not_none(payload, "aspect_ratio", aspect_ratio)
        _add_if_not_none(payload, "duration", duration)
        _add_if_not_none(payload, "negative_prompt", negative_prompt)
        _add_if_not_none(payload, "seed", seed)
        _add_if_not_none(payload, "enhance_prompt", enhance_prompt)

        base_url = self._client.base_url
        create_url = _video_api_url(base_url, _VIDEO_GENERATION_CREATE_PATH)
        job = self._post(
            create_url,
            body=payload,
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
            ),
            cast_to=object,
            stream=False,
        )

        job_payload = _coerce_mapping(job, context="video generation create")
        if status_callback is not None:
            status_callback(job_payload)

        generation_id = _extract_generation_id(job_payload)
        if not generation_id:
            raise RuntimeError("Video generation response did not include a generation_id")

        status_template = _video_api_url(base_url, _VIDEO_GENERATION_STATUS_PATH)
        result = poll_job(
            self,
            path_template=status_template,
            generation_id=generation_id,
            poll_interval=poll_interval,
            poll_timeout=poll_timeout,
            request_timeout=timeout,
            status_callback=status_callback,
            pending_statuses=_VIDEO_PENDING_STATUSES,
        )

        return _coerce_mapping(result, context="video generation status")


class AsyncVideos(OpenAIAsyncVideos):
    """Async AIMLAPI specific video helpers."""

    async def generate_with_polling(
        self,
        *,
        model: str,
        prompt: str,
        aspect_ratio: str | None = None,
        duration: int | None = None,
        negative_prompt: str | None = None,
        seed: int | None = None,
        enhance_prompt: bool | None = None,
        poll_interval: float = _DEFAULT_POLL_INTERVAL,
        poll_timeout: float | None = _DEFAULT_POLL_TIMEOUT,
        status_callback: Callable[[Mapping[str, Any]], None] | None = None,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "model": model,
            "prompt": prompt,
        }
        _add_if_not_none(payload, "aspect_ratio", aspect_ratio)
        _add_if_not_none(payload, "duration", duration)
        _add_if_not_none(payload, "negative_prompt", negative_prompt)
        _add_if_not_none(payload, "seed", seed)
        _add_if_not_none(payload, "enhance_prompt", enhance_prompt)

        base_url = self._client.base_url
        create_url = _video_api_url(base_url, _VIDEO_GENERATION_CREATE_PATH)
        job = await self._post(
            create_url,
            body=payload,
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
            ),
            cast_to=object,
            stream=False,
        )

        job_payload = _coerce_mapping(job, context="video generation create")
        if status_callback is not None:
            status_callback(job_payload)

        generation_id = _extract_generation_id(job_payload)
        if not generation_id:
            raise RuntimeError("Video generation response did not include a generation_id")

        status_template = _video_api_url(base_url, _VIDEO_GENERATION_STATUS_PATH)
        result = await async_poll_job(
            self,
            path_template=status_template,
            generation_id=generation_id,
            poll_interval=poll_interval,
            poll_timeout=poll_timeout,
            request_timeout=timeout,
            status_callback=status_callback,
            pending_statuses=_VIDEO_PENDING_STATUSES,
        )

        return _coerce_mapping(result, context="video generation status")

