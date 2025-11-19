from __future__ import annotations

import json

import httpx
import pytest
from respx import MockRouter

from .conftest import AIML_BASE_URL


@pytest.mark.respx(base_url=AIML_BASE_URL)
def test_completion_request_shape(aiml_client, respx_mock: MockRouter) -> None:
    route = respx_mock.post("/completions").mock(
        return_value=httpx.Response(
            200,
            json={
                "id": "cmpl",
                "object": "text_completion",
                "choices": [
                    {
                        "index": 0,
                        "finish_reason": "stop",
                        "text": "AIMLAPI rocks",
                    }
                ],
                "created": 0,
                "model": "gpt-4o-mini",
            },
        )
    )

    completion = aiml_client.completions.create(model="gpt-4o-mini", prompt="ping")

    assert completion.choices[0].text.startswith("AIMLAPI")
    assert route.called
    payload = json.loads(route.calls[0].request.content.decode())
    assert payload == {"model": "gpt-4o-mini", "prompt": "ping"}
