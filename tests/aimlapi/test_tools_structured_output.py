from __future__ import annotations

import json

import httpx
import pytest
from pydantic import BaseModel
from respx import MockRouter

from openai.lib._tools import ResponsesPydanticFunctionTool

from .conftest import AIML_BASE_URL
from .helpers import function_response_payload, response_payload


class LookupArgs(BaseModel):
    city: str


@pytest.mark.respx(base_url=AIML_BASE_URL)
def test_tool_schema_is_cleaned(aiml_client, respx_mock: MockRouter) -> None:
    raw_tool = {
        "type": "function",
        "function": {
            "name": "lookup_city",
            "strict": True,
            "parameters": {
                "title": "Weather",
                "$defs": {"unused": {}},
                "type": "object",
                "properties": {"city": {"type": "string"}},
            },
        },
    }
    route = respx_mock.post("/responses").mock(return_value=httpx.Response(200, json=response_payload()))

    aiml_client.responses.create(input="Where?", model="gpt-4o-mini", tools=[raw_tool])

    payload = json.loads(route.calls[0].request.content.decode())
    cleaned = payload["tools"][0]["function"]
    assert "strict" not in cleaned
    assert "title" not in cleaned["parameters"]
    assert "$defs" not in cleaned["parameters"]


@pytest.mark.respx(base_url=AIML_BASE_URL)
def test_parsed_tool_arguments(aiml_client, respx_mock: MockRouter) -> None:
    tool = ResponsesPydanticFunctionTool(
        {
            "type": "function",
            "name": "lookup_city",
            "description": "Look up a city",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
            },
            "strict": True,
        },
        LookupArgs,
    )
    payload = function_response_payload(arguments='{"city": "Lisbon"}')
    respx_mock.post("/responses").mock(return_value=httpx.Response(200, json=payload))

    parsed = aiml_client.responses.parse(
        model="gpt-4o-mini",
        input="Call the tool",
        tools=[tool],
    )

    call = parsed.output[0]
    assert call.type == "function_call"
    assert call.parsed_arguments and call.parsed_arguments.city == "Lisbon"
