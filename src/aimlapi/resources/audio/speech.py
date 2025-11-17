from __future__ import annotations

import base64
import binascii
from dataclasses import dataclass
from typing import Any, Dict, Mapping, Union

import httpx
from typing_extensions import Literal, override

from openai import _legacy_response
from openai._base_client import make_request_options
from openai._response import AsyncStreamedBinaryAPIResponse, StreamedBinaryAPIResponse
from openai._types import Body, Headers, NotGiven, Omit, Query, Timeout, omit, not_given
from openai.resources.audio.speech import (
    AsyncSpeech as OpenAIAsyncSpeech,
    AsyncSpeechWithRawResponse,
    AsyncSpeechWithStreamingResponse,
    Speech as OpenAISpeech,
    SpeechWithRawResponse,
    SpeechWithStreamingResponse,
)
from openai.types.audio.speech_model import SpeechModel

__all__ = [
    "Speech",
    "AsyncSpeech",
    "SpeechWithRawResponse",
    "AsyncSpeechWithRawResponse",
    "SpeechWithStreamingResponse",
    "AsyncSpeechWithStreamingResponse",
]

_TTS_CREATE_PATH = "/tts"
_AUDIO_MIME_TYPES = {
    "mp3": "audio/mpeg",
    "opus": "audio/opus",
    "aac": "audio/aac",
    "flac": "audio/flac",
    "wav": "audio/wav",
    "pcm": "audio/pcm",
}


class Speech(OpenAISpeech):
    """AIMLAPI specific TTS helpers."""

    @override
    def create(
        self,
        *,
        input: str,
        model: Union[str, SpeechModel],
        voice: Union[
            str,
            Literal[
                "alloy",
                "ash",
                "ballad",
                "coral",
                "echo",
                "fable",
                "nova",
                "onyx",
                "sage",
                "shimmer",
                "verse",
            ],
        ],
        instructions: str | Omit = omit,
        response_format: Literal["mp3", "opus", "aac", "flac", "wav", "pcm"] | Omit = omit,
        speed: float | Omit = omit,
        stream_format: Literal["sse", "audio"] | Omit = omit,
        wait: bool = True,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
    ) -> Union[_legacy_response.HttpxBinaryResponseContent, Dict[str, Any]]:
        if not isinstance(stream_format, Omit):
            raise ValueError("AIMLAPI text-to-speech does not support streaming output yet.")

        payload: Dict[str, Any] = {
            "text": input,
            "model": str(model),
            "voice": str(voice),
        }
        _add_if_given(payload, "style", instructions)
        _add_if_given(payload, "response_format", response_format)
        _add_if_given(payload, "speed", speed)

        job = self._post(
            _TTS_CREATE_PATH,
            body=payload,
            options=make_request_options(
                extra_body=extra_body,
                extra_headers=extra_headers,
                extra_query=extra_query,
                timeout=timeout,
            ),
            cast_to=object,
            stream=False,
        )

        if not wait:
            return _coerce_mapping(job)

        return _finalize_sync_tts_payload(
            resource=self,
            payload=job,
            response_format=response_format,
            timeout=timeout,
        )


class AsyncSpeech(OpenAIAsyncSpeech):
    """Async AIMLAPI specific TTS helpers."""

    @override
    async def create(
        self,
        *,
        input: str,
        model: Union[str, SpeechModel],
        voice: Union[
            str,
            Literal[
                "alloy",
                "ash",
                "ballad",
                "coral",
                "echo",
                "fable",
                "nova",
                "onyx",
                "sage",
                "shimmer",
                "verse",
            ],
        ],
        instructions: str | Omit = omit,
        response_format: Literal["mp3", "opus", "aac", "flac", "wav", "pcm"] | Omit = omit,
        speed: float | Omit = omit,
        stream_format: Literal["sse", "audio"] | Omit = omit,
        wait: bool = True,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
    ) -> Union[_legacy_response.HttpxBinaryResponseContent, Dict[str, Any]]:
        if not isinstance(stream_format, Omit):
            raise ValueError("AIMLAPI text-to-speech does not support streaming output yet.")

        payload: Dict[str, Any] = {
            "text": input,
            "model": str(model),
            "voice": str(voice),
        }
        _add_if_given(payload, "style", instructions)
        _add_if_given(payload, "response_format", response_format)
        _add_if_given(payload, "speed", speed)

        job = await self._post(
            _TTS_CREATE_PATH,
            body=payload,
            options=make_request_options(
                extra_body=extra_body,
                extra_headers=extra_headers,
                extra_query=extra_query,
                timeout=timeout,
            ),
            cast_to=object,
            stream=False,
        )

        if not wait:
            return _coerce_mapping(job)

        return await _finalize_async_tts_payload(
            resource=self,
            payload=job,
            response_format=response_format,
            timeout=timeout,
        )


def _add_if_given(payload: Dict[str, Any], key: str, value: object) -> None:
    if not isinstance(value, Omit):
        payload[key] = value


@dataclass
class _InlineAudio:
    data: bytes
    mime: str | None


@dataclass
class _AudioURL:
    url: str
    mime: str | None


def _finalize_sync_tts_payload(
    *,
    resource: Speech,
    payload: object,
    response_format: Literal["mp3", "opus", "aac", "flac", "wav", "pcm"] | Omit,
    timeout: float | Timeout | None | NotGiven,
) -> Union[_legacy_response.HttpxBinaryResponseContent, Dict[str, Any]]:
    # Short-circuit if the payload is already a streamed binary response
    if isinstance(payload, StreamedBinaryAPIResponse):
        return payload  # type: ignore[return-value]

    mapping = _coerce_mapping(payload)
    audio_reference = _extract_audio_payload(mapping)
    if audio_reference is None:
        return mapping

    data, mime = _resolve_audio_reference(resource, audio_reference, timeout)
    return _wrap_audio_bytes(data, mime, response_format)


async def _finalize_async_tts_payload(
    *,
    resource: AsyncSpeech,
    payload: object,
    response_format: Literal["mp3", "opus", "aac", "flac", "wav", "pcm"] | Omit,
    timeout: float | Timeout | None | NotGiven,
) -> Union[_legacy_response.HttpxBinaryResponseContent, Dict[str, Any]]:
    # Short-circuit if the payload is already a streamed binary response
    if isinstance(payload, AsyncStreamedBinaryAPIResponse):
        return payload  # type: ignore[return-value]

    mapping = _coerce_mapping(payload)
    audio_reference = _extract_audio_payload(mapping)
    if audio_reference is None:
        return mapping

    data, mime = await _async_resolve_audio_reference(resource, audio_reference, timeout)
    return _wrap_audio_bytes(data, mime, response_format)


def _wrap_audio_bytes(
    data: bytes,
    mime: str | None,
    response_format: Literal["mp3", "opus", "aac", "flac", "wav", "pcm"] | Omit,
) -> _legacy_response.HttpxBinaryResponseContent:
    fmt = None if isinstance(response_format, Omit) else response_format
    content_type = mime or _AUDIO_MIME_TYPES.get(fmt or "mp3", "application/octet-stream")
    response = httpx.Response(200, content=data, headers={"content-type": content_type})
    return _legacy_response.HttpxBinaryResponseContent(response)


def _resolve_audio_reference(
    resource: Speech,
    reference: _InlineAudio | _AudioURL,
    timeout: float | Timeout | None | NotGiven,
) -> tuple[bytes, str | None]:
    if isinstance(reference, _InlineAudio):
        return reference.data, reference.mime

    return _download_audio_from_url(resource, reference.url, reference.mime, timeout)


async def _async_resolve_audio_reference(
    resource: AsyncSpeech,
    reference: _InlineAudio | _AudioURL,
    timeout: float | Timeout | None | NotGiven,
) -> tuple[bytes, str | None]:
    if isinstance(reference, _InlineAudio):
        return reference.data, reference.mime

    return await _async_download_audio_from_url(resource, reference.url, reference.mime, timeout)


def _extract_audio_payload(payload: object) -> _InlineAudio | _AudioURL | None:
    return _walk_for_audio(payload, expect_audio=False, mime_hint=None)


def _walk_for_audio(
    value: object,
    *,
    expect_audio: bool,
    mime_hint: str | None,
) -> _InlineAudio | _AudioURL | None:
    if isinstance(value, Mapping):
        next_mime = mime_hint
        if expect_audio:
            mime_value = value.get("mime_type") or value.get("content_type") or value.get("type")
            if isinstance(mime_value, str) and mime_value.startswith("audio/"):
                next_mime = mime_value

            url_value = value.get("url") or value.get("href")
            if isinstance(url_value, str) and _looks_like_url(url_value):
                return _AudioURL(url=url_value, mime=next_mime)

        for key, child in value.items():
            key_lower = key.lower() if isinstance(key, str) else str(key).lower()
            child_expect_audio = expect_audio or key_lower in {
                "audio",
                "audio_data",
                "audio_bytes",
                "audio_content",
                "audiofile",
                "sound",
            }
            result = _walk_for_audio(child, expect_audio=child_expect_audio, mime_hint=next_mime)
            if result is not None:
                return result
        return None

    if isinstance(value, list):
        for item in value:
            result = _walk_for_audio(item, expect_audio=expect_audio, mime_hint=mime_hint)
            if result is not None:
                return result
        return None

    if expect_audio:
        if isinstance(value, bytes):
            return _InlineAudio(data=value, mime=mime_hint)
        if isinstance(value, str):
            url = _looks_like_url(value)
            if url:
                return _AudioURL(url=value, mime=mime_hint)

            decoded = _decode_audio_string(value)
            if decoded is not None:
                data, inferred_mime = decoded
                return _InlineAudio(data=data, mime=inferred_mime or mime_hint)

    return None


def _decode_audio_string(value: str) -> tuple[bytes, str | None] | None:
    text = value.strip()

    if text.startswith("data:audio"):
        header, _, encoded = text.partition(",")
        if not encoded:
            return None
        mime = None
        header_meta = header.split(";", 1)[0]
        if ":" in header_meta:
            mime = header_meta.split(":", 1)[1]
        try:
            return base64.b64decode(encoded, validate=True), mime
        except binascii.Error:
            return None

    normalized = text.replace("\n", "").replace(" ", "")
    try:
        return base64.b64decode(normalized, validate=True), None
    except binascii.Error:
        return None


def _coerce_mapping(value: object) -> Dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    print('err', value)
    raise TypeError("Unexpected response payload from TTS endpoint")


def _looks_like_url(value: str) -> bool:
    text = value.strip().lower()
    return text.startswith("http://") or text.startswith("https://")


def _download_audio_from_url(
    resource: Speech,
    url: str,
    mime_hint: str | None,
    timeout: float | Timeout | None | NotGiven,
) -> tuple[bytes, str | None]:
    http_client = resource._client._client  # type: ignore[attr-defined]
    headers = {"Accept": "*/*", **resource._client.auth_headers}
    response = http_client.get(url, headers=headers, timeout=_coerce_timeout(timeout))
    response.raise_for_status()
    content_type = response.headers.get("content-type") or mime_hint
    return response.content, content_type


async def _async_download_audio_from_url(
    resource: AsyncSpeech,
    url: str,
    mime_hint: str | None,
    timeout: float | Timeout | None | NotGiven,
) -> tuple[bytes, str | None]:
    http_client = resource._client._client  # type: ignore[attr-defined]
    headers = {"Accept": "*/*", **resource._client.auth_headers}
    response = await http_client.get(url, headers=headers, timeout=_coerce_timeout(timeout))
    response.raise_for_status()
    content_type = response.headers.get("content-type") or mime_hint
    return response.content, content_type


def _coerce_timeout(value: float | Timeout | None | NotGiven) -> float | Timeout | None:
    return None if isinstance(value, NotGiven) else value

