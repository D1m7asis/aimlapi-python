from __future__ import annotations

import json

import httpx
import pytest
from respx import MockRouter

from .conftest import AIML_BASE_URL


@pytest.mark.respx(base_url=AIML_BASE_URL)
def test_chat_completion_request_body(aiml_client, respx_mock: MockRouter) -> None:
    route = respx_mock.post("/chat/completions").mock(
        return_value=httpx.Response(
            200,
            json={
                "id": "chatcmpl",
                "object": "chat.completion",
                "choices": [
                    {
                        "index": 0,
                        "finish_reason": "stop",
                        "message": {"role": "assistant", "content": "hi"},
                    }
                ],
                "created": 0,
                "model": "gpt-4o-mini",
            },
        )
    )

    result = aiml_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Hello"}],
    )

    assert result.choices[0].message.content == "hi"
    assert route.called
    payload = json.loads(route.calls[0].request.content.decode())
    assert payload["model"] == "gpt-4o-mini"
    assert payload["messages"][0]["content"] == "Hello"
