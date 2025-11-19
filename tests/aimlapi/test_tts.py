from __future__ import annotations

import base64
import json

import httpx
import pytest
from respx import MockRouter

from .conftest import AIML_BASE_URL


@pytest.mark.respx(base_url=AIML_BASE_URL)
def test_tts_wait_false_returns_job(aiml_client, respx_mock: MockRouter) -> None:
    job = {"id": "tts_1", "status": "queued"}
    route = respx_mock.post("/tts").mock(return_value=httpx.Response(200, json=job))

    result = aiml_client.audio.speech.create(
        model="minimax/speech-2.5-turbo-preview",
        voice="Vince Douglas",
        input="Hello",
        wait=False,
    )

    assert result == job
    payload = route.calls[0].request.content
    assert payload
    assert json.loads(payload.decode()) == {
        "text": "Hello",
        "model": "minimax/speech-2.5-turbo-preview",
        "voice": "Vince Douglas",
    }


@pytest.mark.respx(base_url=AIML_BASE_URL)
def test_tts_inline_audio_returns_binary(aiml_client, respx_mock: MockRouter) -> None:
    audio_bytes = base64.b64encode(b"hello").decode()
    respx_mock.post("/tts").mock(
        return_value=httpx.Response(200, json={"audio": {"data": audio_bytes, "mime_type": "audio/wav"}})
    )

    response = aiml_client.audio.speech.create(
        model="minimax/speech-2.5-turbo-preview",
        voice="Vince Douglas",
        input="Hello",
    )

    assert response.read() == b"hello"
    assert response.response.headers["content-type"] == "audio/wav"
