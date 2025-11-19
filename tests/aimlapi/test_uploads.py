from __future__ import annotations

from pathlib import Path

import httpx
import pytest
from respx import MockRouter

from .conftest import AIML_BASE_URL


@pytest.mark.respx(base_url=AIML_BASE_URL)
def test_chunked_upload_uses_multiple_parts(
    tmp_path: Path, aiml_client, respx_mock: MockRouter
) -> None:
    data = b"abcdefghij"
    file_path = tmp_path / "demo.bin"
    file_path.write_bytes(data)

    respx_mock.post("/uploads").mock(
        return_value=httpx.Response(
            200,
            json={
                "id": "upl_1",
                "bytes": len(data),
                "filename": file_path.name,
                "object": "upload",
                "purpose": "batch",
                "created_at": 0,
                "expires_at": 1,
                "status": "pending",
            },
        )
    )

    part_ids = iter(["part_1", "part_2", "part_3"])

    def part_response(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"id": next(part_ids), "object": "upload.part", "upload_id": "upl_1", "created_at": 0},
        )

    parts_route = respx_mock.post("/uploads/upl_1/parts").mock(side_effect=part_response)

    respx_mock.post("/uploads/upl_1/complete").mock(
        return_value=httpx.Response(
            200,
            json={
                "id": "upl_1",
                "bytes": len(data),
                "filename": file_path.name,
                "object": "upload",
                "purpose": "batch",
                "created_at": 0,
                "expires_at": 1,
                "status": "completed",
            },
        )
    )

    result = aiml_client.uploads.upload_file_chunked(
        file=file_path,
        mime_type="txt",
        purpose="batch",
        part_size=4,
    )

    assert result.status == "completed"
    assert parts_route.call_count == 3
