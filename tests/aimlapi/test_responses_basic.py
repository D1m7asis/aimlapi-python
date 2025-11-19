from __future__ import annotations

import json

import httpx
import pytest
from pydantic import BaseModel
from respx import MockRouter

from .conftest import AIML_BASE_URL
from .helpers import response_payload


class MathResult(BaseModel):
    answer: int


@pytest.mark.respx(base_url=AIML_BASE_URL)
def test_responses_parse_returns_structured_output(aiml_client, respx_mock: MockRouter) -> None:
    payload = response_payload(text="{\"answer\": 42}")
    route = respx_mock.post("/responses").mock(return_value=httpx.Response(200, json=payload))

    parsed = aiml_client.responses.parse(
        model="gpt-4o-mini",
        input="2+2",
        text_format=MathResult,
    )

    result = parsed.output[0]
    assert result.type == "message"
    assert result.content[0].parsed and result.content[0].parsed.answer == 42

    sent = json.loads(route.calls[0].request.content.decode())
    assert sent["text"]["format"]["type"] == "json_schema"
