from __future__ import annotations

import httpx
import pytest
from respx import MockRouter

from .conftest import AIML_BASE_URL


@pytest.mark.respx(base_url=AIML_BASE_URL)
def test_image_generation_payload(aiml_client, respx_mock: MockRouter) -> None:
    route = respx_mock.post("/images/generations").mock(
        return_value=httpx.Response(200, json={"data": [{"url": "https://img"}]})
    )

    image = aiml_client.images.generate(model="gpt-image-1", prompt="a lighthouse")

    assert image.data[0].url == "https://img"
    request = route.calls[0].request
    assert request.headers["content-type"] == "application/json"


@pytest.mark.respx(base_url=AIML_BASE_URL)
def test_image_edit_is_multipart(aiml_client, respx_mock: MockRouter) -> None:
    route = respx_mock.post("/images/edits").mock(
        return_value=httpx.Response(200, json={"data": [{"b64_json": "AA=="}]})
    )

    edit = aiml_client.images.edit(image=b"abc", prompt="fix", mask=b"mask")

    assert edit.data[0].b64_json == "AA=="
    content_type = route.calls[0].request.headers["content-type"].lower()
    assert "multipart/form-data" in content_type
