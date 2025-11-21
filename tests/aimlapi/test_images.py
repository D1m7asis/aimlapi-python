from __future__ import annotations

import base64
import gzip

import httpx
import pytest
from respx import MockRouter

from aimlapi import AsyncAIMLAPI

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


@pytest.mark.respx(base_url=AIML_BASE_URL)
def test_image_generation_b64_json_downloaded(aiml_client, respx_mock: MockRouter) -> None:
    image_bytes = b"png-bytes"

    respx_mock.post("/images/generations").mock(
        return_value=httpx.Response(
            200,
            json={"data": [{"b64_json": None, "url": "https://cdn.example/image.png"}]},
        )
    )
    respx_mock.get("https://cdn.example/image.png").mock(return_value=httpx.Response(200, content=image_bytes))

    image = aiml_client.images.generate(prompt="a lighthouse", response_format="b64_json")

    assert image.data[0].b64_json == base64.b64encode(image_bytes).decode()
    assert image.data[0].url == "https://cdn.example/image.png"


@pytest.mark.respx(base_url=AIML_BASE_URL)
def test_image_generation_b64_json_downloaded_gzipped(aiml_client, respx_mock: MockRouter) -> None:
    image_bytes = b"png-bytes"
    gzipped_bytes = gzip.compress(image_bytes)

    respx_mock.post("/images/generations").mock(
        return_value=httpx.Response(
            200,
            json={"data": [{"b64_json": None, "url": "https://cdn.example/image.png"}]},
        )
    )
    respx_mock.get("https://cdn.example/image.png").mock(
        return_value=httpx.Response(200, content=gzipped_bytes, headers={"content-encoding": "gzip"})
    )

    image = aiml_client.images.generate(prompt="a lighthouse", response_format="b64_json")

    assert image.data[0].b64_json == base64.b64encode(image_bytes).decode()
    assert image.data[0].url == "https://cdn.example/image.png"


@pytest.mark.respx(base_url=AIML_BASE_URL)
def test_image_generation_b64_json_download_failure(aiml_client, respx_mock: MockRouter) -> None:
    respx_mock.post("/images/generations").mock(
        return_value=httpx.Response(
            200,
            json={"data": [{"b64_json": None, "url": "https://cdn.example/image.png"}]},
        )
    )
    respx_mock.get("https://cdn.example/image.png").mock(return_value=httpx.Response(500))

    image = aiml_client.images.generate(prompt="a lighthouse", response_format="b64_json")

    assert image.data[0].b64_json is None
    assert image.data[0].url == "https://cdn.example/image.png"


@pytest.mark.asyncio
@pytest.mark.respx(base_url=AIML_BASE_URL)
async def test_async_image_generation_b64_json_downloaded(respx_mock: MockRouter) -> None:
    image_bytes = b"async-bytes"
    client = AsyncAIMLAPI(api_key="test", base_url=AIML_BASE_URL)

    try:
        respx_mock.post("/images/generations").mock(
            return_value=httpx.Response(
                200,
                json={"data": [{"b64_json": None, "url": "https://cdn.example/image.png"}]},
            )
        )
        respx_mock.get("https://cdn.example/image.png").mock(
            return_value=httpx.Response(200, content=image_bytes)
        )

        image = await client.images.generate(prompt="a lighthouse", response_format="b64_json")

        assert image.data[0].b64_json == base64.b64encode(image_bytes).decode()
        assert image.data[0].url == "https://cdn.example/image.png"
    finally:
        await client.close()
