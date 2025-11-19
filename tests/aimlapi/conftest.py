from __future__ import annotations

import pytest

from aimlapi import AIMLAPI

AIML_BASE_URL = "https://example.aimlapi"


@pytest.fixture
def aiml_client() -> AIMLAPI:
    client = AIMLAPI(api_key="test", base_url=AIML_BASE_URL)
    try:
        yield client
    finally:
        client.close()
