from __future__ import annotations

import httpx
import pytest
from respx import MockRouter

from .conftest import AIML_BASE_URL
from .helpers import response_payload, sse_bytes
from .test_responses_basic import MathResult


@pytest.mark.respx(base_url=AIML_BASE_URL)
def test_responses_stream_emits_events(aiml_client, respx_mock: MockRouter) -> None:
    initial = response_payload(text="")
    final = response_payload(text="{\"answer\": 42}")
    events = [
        (
            "response.created",
            {"type": "response.created", "sequence_number": 1, "response": initial},
        ),
        (
            "response.output_text.delta",
            {
                "type": "response.output_text.delta",
                "sequence_number": 2,
                "item_id": "msg_1",
                "output_index": 0,
                "content_index": 0,
                "delta": "{\"answer\": 4",
                "logprobs": [],
            },
        ),
        (
            "response.output_text.done",
            {
                "type": "response.output_text.done",
                "sequence_number": 3,
                "item_id": "msg_1",
                "output_index": 0,
                "content_index": 0,
                "text": "{\"answer\": 42}",
                "logprobs": [],
            },
        ),
        (
            "response.completed",
            {"type": "response.completed", "sequence_number": 4, "response": final},
        ),
    ]
    respx_mock.post("/responses").mock(
        return_value=httpx.Response(
            200,
            headers={"Content-Type": "text/event-stream"},
            content=sse_bytes(events),
        )
    )

    with aiml_client.responses.stream(
        input="solve", model="gpt-4o-mini", text_format=MathResult
    ) as stream:
        collected = list(stream)
        event_types = [event.type for event in collected]
        assert event_types[0] == "response.created"
        assert "response.output_text.delta" in event_types
        assert event_types[-1] == "response.completed"
        final_response = stream.get_final_response()

    assert final_response.output[0].content[0].parsed
    assert final_response.output[0].content[0].parsed.answer == 42
