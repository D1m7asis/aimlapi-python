from __future__ import annotations

from openai._compat import cached_property
from openai.resources.audio.audio import (
    Audio as OpenAIAudio,
    AsyncAudio as OpenAIAsyncAudio,
    AudioWithRawResponse,
    AsyncAudioWithRawResponse,
    AudioWithStreamingResponse,
    AsyncAudioWithStreamingResponse,
)
from openai.resources.audio.translations import AsyncTranslations, Translations

from .speech import AsyncSpeech, Speech
from .transcriptions import AsyncTranscriptions, Transcriptions

__all__ = [
    "Audio",
    "AsyncAudio",
    "AudioWithRawResponse",
    "AsyncAudioWithRawResponse",
    "AudioWithStreamingResponse",
    "AsyncAudioWithStreamingResponse",
]


class Audio(OpenAIAudio):
    @cached_property
    def transcriptions(self) -> Transcriptions:
        return Transcriptions(self._client)

    @cached_property
    def translations(self) -> Translations:
        return Translations(self._client)

    @cached_property
    def speech(self) -> Speech:
        return Speech(self._client)


class AsyncAudio(OpenAIAsyncAudio):
    @cached_property
    def transcriptions(self) -> AsyncTranscriptions:
        return AsyncTranscriptions(self._client)

    @cached_property
    def translations(self) -> AsyncTranslations:
        return AsyncTranslations(self._client)

    @cached_property
    def speech(self) -> AsyncSpeech:
        return AsyncSpeech(self._client)

