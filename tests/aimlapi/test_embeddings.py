from __future__ import annotations

import json

import httpx
import pytest
from respx import MockRouter

from .conftest import AIML_BASE_URL


@pytest.mark.respx(base_url=AIML_BASE_URL)
def test_embeddings_call(aiml_client, respx_mock: MockRouter) -> None:
    route = respx_mock.post("/embeddings").mock(
        return_value=httpx.Response(
            200,
            json={
                "object": "list",
                "data": [
                    {"object": "embedding", "embedding": [0.1, 0.2], "index": 0},
                ],
                "model": "text-embedding-3-small",
            },
        )
    )

    emb = aiml_client.embeddings.create(model="text-embedding-3-small", input="A cat")

    assert emb.data[0].embedding == [0.1, 0.2]
    payload = json.loads(route.calls[0].request.content.decode())
    assert payload["model"] == "text-embedding-3-small"
    assert payload["input"] == "A cat"
    assert payload["encoding_format"] == "base64"
