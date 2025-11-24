from __future__ import annotations

from typing import Any

from openai._base_client import BaseClient

from openai.resources.uploads.uploads import (
    AsyncUploads as OpenAIAsyncUploads,
    AsyncUploadsWithRawResponse,
    AsyncUploadsWithStreamingResponse,
    Uploads as OpenAIUploads,
    UploadsWithRawResponse,
    UploadsWithStreamingResponse,
)

__all__ = [
    "Uploads",
    "AsyncUploads",
    "UploadsWithRawResponse",
    "AsyncUploadsWithRawResponse",
    "UploadsWithStreamingResponse",
    "AsyncUploadsWithStreamingResponse",
]


def _files_path(path: str) -> str:
    if path.startswith("/v1/files"):
        return path[len("/v1") :]

    if path.startswith("/files"):
        return path

    if path.startswith("/v1/uploads"):
        suffix = path[len("/v1/uploads") :]
        return f"/files{suffix}"

    if path.startswith("/uploads"):
        suffix = path[len("/uploads") :]
        return f"/files{suffix}"

    return path


def _files_base_url(client: BaseClient) -> str:
    """Return a base URL stripped of any trailing /v1 segment."""

    base_url = str(client.base_url)

    if base_url.endswith("/v1/"):
        return base_url[: -len("/v1/")]

    if base_url.endswith("/v1"):
        return base_url[: -len("/v1")]

    if base_url.endswith("/"):
        return base_url[:-1]

    return base_url


def _files_url(client: BaseClient, path: str) -> str:
    base_url = _files_base_url(client)
    if path.startswith("/"):
        return f"{base_url}{path}"
    return f"{base_url}/{path}"


class Uploads(OpenAIUploads):
    def __init__(self, client: Any) -> None:
        super().__init__(client)
        self._post = self._files_post  # type: ignore[assignment]
        self._get = self._files_get  # type: ignore[assignment]

    def _files_post(self, path: str, **kwargs: Any):
        path = _files_path(path)
        url = _files_url(self._client, path)
        return self._client.post(url, **kwargs)  # type: ignore[misc]

    def _files_get(self, path: str, **kwargs: Any):
        path = _files_path(path)
        url = _files_url(self._client, path)
        return self._client.get(url, **kwargs)  # type: ignore[misc]


class AsyncUploads(OpenAIAsyncUploads):
    def __init__(self, client: Any) -> None:
        super().__init__(client)
        self._post = self._files_post  # type: ignore[assignment]
        self._get = self._files_get  # type: ignore[assignment]

    async def _files_post(self, path: str, **kwargs: Any):
        path = _files_path(path)
        url = _files_url(self._client, path)
        return await self._client.post(url, **kwargs)  # type: ignore[misc]

    async def _files_get(self, path: str, **kwargs: Any):
        path = _files_path(path)
        url = _files_url(self._client, path)
        return await self._client.get(url, **kwargs)  # type: ignore[misc]
