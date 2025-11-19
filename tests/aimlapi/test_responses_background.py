from __future__ import annotations

import httpx
import pytest
from respx import MockRouter

from .conftest import AIML_BASE_URL
from .helpers import response_payload, sse_bytes


@pytest.mark.respx(base_url=AIML_BASE_URL)
def test_background_retrieve_stream(aiml_client, respx_mock: MockRouter) -> None:
    final = response_payload(text="{\"answer\": 42}")
    events = [
        (
            "response.created",
            {"type": "response.created", "sequence_number": 10, "response": final},
        ),
        (
            "response.completed",
            {"type": "response.completed", "sequence_number": 11, "response": final},
        ),
    ]
    route = respx_mock.get("/responses/resp_bg").mock(
        return_value=httpx.Response(
            200,
            headers={"Content-Type": "text/event-stream"},
            content=sse_bytes(events),
        )
    )

    with aiml_client.responses.retrieve(
        "resp_bg", stream=True, starting_after=5
    ) as stream:
        received = list(stream)

    assert received[-1].type == "response.completed"
    params = route.calls[0].request.url.params
    assert params["stream"] == "true"
    assert params["starting_after"] == "5"
