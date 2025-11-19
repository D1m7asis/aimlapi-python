from __future__ import annotations

import httpx
import pytest
from respx import MockRouter

from aimlapi import AuthenticationError, BadRequestError

from .conftest import AIML_BASE_URL


@pytest.mark.respx(base_url=AIML_BASE_URL)
def test_bad_request_error_surface(aiml_client, respx_mock: MockRouter) -> None:
    respx_mock.post("/chat/completions").mock(
        return_value=httpx.Response(
            400,
            json={"error": {"message": "missing", "type": "invalid_request_error"}},
        )
    )

    with pytest.raises(BadRequestError):
        aiml_client.chat.completions.create(model="gpt-4o-mini", messages=[])


@pytest.mark.respx(base_url=AIML_BASE_URL)
def test_authentication_error_surface(aiml_client, respx_mock: MockRouter) -> None:
    respx_mock.post("/chat/completions").mock(
        return_value=httpx.Response(401, json={"error": {"message": "bad key"}})
    )

    with pytest.raises(AuthenticationError):
        aiml_client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": "hi"}])
