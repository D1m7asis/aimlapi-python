from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional, Sequence, Union

from typing_extensions import Literal, override

from openai._base_client import make_request_options
from openai._types import (
    Body,
    FileTypes,
    Headers,
    NotGiven,
    Omit,
    Query,
    SequenceNotStr,
    Timeout,
    omit,
    not_given,
)
from openai._utils import required_args
from openai.resources.audio.transcriptions import (
    AsyncTranscriptions as OpenAIAsyncTranscriptions,
    AsyncTranscriptionsWithRawResponse,
    AsyncTranscriptionsWithStreamingResponse,
    Transcriptions as OpenAITranscriptions,
    TranscriptionsWithRawResponse,
    TranscriptionsWithStreamingResponse,
)
from openai.types.audio import transcription_create_params
from openai.types.audio.transcription_include import TranscriptionInclude
from openai.types.audio_model import AudioModel
from openai.types.audio_response_format import AudioResponseFormat

from ._polling import async_poll_job, poll_job

__all__ = [
    "Transcriptions",
    "AsyncTranscriptions",
    "TranscriptionsWithRawResponse",
    "AsyncTranscriptionsWithRawResponse",
    "TranscriptionsWithStreamingResponse",
    "AsyncTranscriptionsWithStreamingResponse",
]

_STT_CREATE_PATH = "/stt/create"
_STT_STATUS_PATH = "/stt/{generation_id}"
_DEFAULT_POLL_INTERVAL = 5.0
_DEFAULT_POLL_TIMEOUT = 600.0


def _add_if_given(payload: Dict[str, Any], key: str, value: object) -> None:
    if not isinstance(value, Omit):
        payload[key] = value


class Transcriptions(OpenAITranscriptions):
    """AIMLAPI specific transcription helpers."""

    @override
    @required_args(["file", "model"], ["file", "model", "stream"])
    def create(
        self,
        *,
        file: FileTypes,
        model: Union[str, AudioModel],
        chunking_strategy: Optional[transcription_create_params.ChunkingStrategy] | Omit = omit,
        include: List[TranscriptionInclude] | Omit = omit,
        known_speaker_names: SequenceNotStr[str] | Omit = omit,
        known_speaker_references: SequenceNotStr[str] | Omit = omit,
        language: str | Omit = omit,
        prompt: str | Omit = omit,
        response_format: Union[AudioResponseFormat, Omit] = omit,
        stream: Optional[Literal[False]] | Literal[True] | Omit = omit,
        temperature: float | Omit = omit,
        timestamp_granularities: List[Literal["word", "segment"]] | Omit = omit,
        wait: bool = True,
        poll_interval: float = _DEFAULT_POLL_INTERVAL,
        poll_timeout: float | None = _DEFAULT_POLL_TIMEOUT,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
    ) -> Dict[str, Any]:
        """Submit audio to AIMLAPI's STT backend and optionally wait for the transcript."""

        data: Dict[str, Any] = {"model": str(model)}
        _add_if_given(data, "chunking_strategy", chunking_strategy)
        _add_if_given(data, "include", include)
        _add_if_given(data, "known_speaker_names", known_speaker_names)
        _add_if_given(data, "known_speaker_references", known_speaker_references)
        _add_if_given(data, "language", language)
        _add_if_given(data, "prompt", prompt)
        _add_if_given(data, "response_format", response_format)
        _add_if_given(data, "stream", stream)
        _add_if_given(data, "temperature", temperature)
        _add_if_given(data, "timestamp_granularities", timestamp_granularities)

        files = {"audio": file}
        headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}

        job = self._post(
            _STT_CREATE_PATH,
            body=data,
            files=files,
            options=make_request_options(
                extra_body=extra_body,
                extra_headers=headers,
                extra_query=extra_query,
                timeout=timeout,
            ),
            cast_to=object,
            stream=False,
        )

        if not wait:
            return job

        generation_id = _extract_generation_id(job)
        if not generation_id:
            return job

        return _coerce_mapping(
            poll_job(
                self,
                path_template=_STT_STATUS_PATH,
                generation_id=generation_id,
                poll_interval=poll_interval,
                poll_timeout=poll_timeout,
                request_timeout=timeout,
            )
        )


class AsyncTranscriptions(OpenAIAsyncTranscriptions):
    """Async AIMLAPI transcription helpers."""

    @override
    @required_args(["file", "model"], ["file", "model", "stream"])
    async def create(
        self,
        *,
        file: FileTypes,
        model: Union[str, AudioModel],
        chunking_strategy: Optional[transcription_create_params.ChunkingStrategy] | Omit = omit,
        include: List[TranscriptionInclude] | Omit = omit,
        known_speaker_names: SequenceNotStr[str] | Omit = omit,
        known_speaker_references: SequenceNotStr[str] | Omit = omit,
        language: str | Omit = omit,
        prompt: str | Omit = omit,
        response_format: Union[AudioResponseFormat, Omit] = omit,
        stream: Optional[Literal[False]] | Literal[True] | Omit = omit,
        temperature: float | Omit = omit,
        timestamp_granularities: List[Literal["word", "segment"]] | Omit = omit,
        wait: bool = True,
        poll_interval: float = _DEFAULT_POLL_INTERVAL,
        poll_timeout: float | None = _DEFAULT_POLL_TIMEOUT,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
    ) -> Dict[str, Any]:
        data: Dict[str, Any] = {"model": str(model)}
        _add_if_given(data, "chunking_strategy", chunking_strategy)
        _add_if_given(data, "include", include)
        _add_if_given(data, "known_speaker_names", known_speaker_names)
        _add_if_given(data, "known_speaker_references", known_speaker_references)
        _add_if_given(data, "language", language)
        _add_if_given(data, "prompt", prompt)
        _add_if_given(data, "response_format", response_format)
        _add_if_given(data, "stream", stream)
        _add_if_given(data, "temperature", temperature)
        _add_if_given(data, "timestamp_granularities", timestamp_granularities)

        files = {"audio": file}
        headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}

        job = await self._post(
            _STT_CREATE_PATH,
            body=data,
            files=files,
            options=make_request_options(
                extra_body=extra_body,
                extra_headers=headers,
                extra_query=extra_query,
                timeout=timeout,
            ),
            cast_to=object,
            stream=False,
        )

        if not wait:
            return job

        generation_id = _extract_generation_id(job)
        if not generation_id:
            return job

        result = await async_poll_job(
            self,
            path_template=_STT_STATUS_PATH,
            generation_id=generation_id,
            poll_interval=poll_interval,
            poll_timeout=poll_timeout,
            request_timeout=timeout,
        )
        return _coerce_mapping(result)


def _extract_generation_id(payload: Mapping[str, Any]) -> str | None:
    generation_id = payload.get("generation_id")
    if isinstance(generation_id, str):
        return generation_id
    return None


def _coerce_mapping(value: object) -> Dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    raise TypeError("Unexpected response payload from STT status endpoint")

