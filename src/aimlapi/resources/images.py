from __future__ import annotations

import base64
from typing import Optional

import httpx
from typing_extensions import Literal, override

from openai.resources import images as _openai_images
from openai.resources.images import *  # noqa: F401, F403
from openai.resources.images import AsyncImages as _OpenAIAsyncImages
from openai.resources.images import Images as _OpenAIImages
from openai._types import NotGiven, not_given
from openai.types import ImagesResponse


class Images(_OpenAIImages):
    @override
    def generate(
        self,
        *,
        prompt: str,
        background: Optional[Literal["transparent", "opaque", "auto"]] | NotGiven = not_given,
        model: str | _openai_images.ImageModel | None | NotGiven = not_given,
        moderation: Optional[Literal["low", "auto"]] | NotGiven = not_given,
        n: Optional[int] | NotGiven = not_given,
        output_compression: Optional[int] | NotGiven = not_given,
        output_format: Optional[Literal["png", "jpeg", "webp"]] | NotGiven = not_given,
        partial_images: Optional[int] | NotGiven = not_given,
        quality: Optional[Literal["standard", "hd", "low", "medium", "high", "auto"]] | NotGiven = not_given,
        response_format: Optional[Literal["url", "b64_json"]] | NotGiven = not_given,
        size: Optional[
            Literal[
                "auto",
                "1024x1024",
                "1536x1024",
                "1024x1536",
                "256x256",
                "512x512",
                "1792x1024",
                "1024x1792",
            ]
        ]
        | NotGiven = not_given,
        stream: Optional[Literal[False]] | Literal[True] | NotGiven = not_given,
        style: Optional[Literal["vivid", "natural"]] | NotGiven = not_given,
        user: str | NotGiven = not_given,
        extra_headers: _openai_images.Headers | None = None,
        extra_query: _openai_images.Query | None = None,
        extra_body: _openai_images.Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ImagesResponse | _openai_images.Stream[_openai_images.ImageGenStreamEvent]:
        response = super().generate(
            prompt=prompt,
            background=background,
            model=model,
            moderation=moderation,
            n=n,
            output_compression=output_compression,
            output_format=output_format,
            partial_images=partial_images,
            quality=quality,
            response_format=response_format,
            size=size,
            stream=stream,
            style=style,
            user=user,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        )

        return self._hydrate_b64_json(response, response_format)

    def _hydrate_b64_json(
        self,
        response: ImagesResponse | _openai_images.Stream[_openai_images.ImageGenStreamEvent],
        response_format: Optional[Literal["url", "b64_json"]] | NotGiven,
    ) -> ImagesResponse | _openai_images.Stream[_openai_images.ImageGenStreamEvent]:
        if response_format != "b64_json" or not isinstance(response, ImagesResponse):
            return response

        images = response.data or []
        missing_b64 = [image for image in images if image.b64_json is None and image.url]
        if not missing_b64:
            return response

        with httpx.Client(follow_redirects=True) as client:
            for image in missing_b64:
                assert image.url  # satisfies type checker
                http_response = client.get(image.url)
                http_response.raise_for_status()
                image.b64_json = base64.b64encode(http_response.content).decode("utf-8")

        return response


class AsyncImages(_OpenAIAsyncImages):
    @override
    async def generate(
        self,
        *,
        prompt: str,
        background: Optional[Literal["transparent", "opaque", "auto"]] | NotGiven = not_given,
        model: str | _openai_images.ImageModel | None | NotGiven = not_given,
        moderation: Optional[Literal["low", "auto"]] | NotGiven = not_given,
        n: Optional[int] | NotGiven = not_given,
        output_compression: Optional[int] | NotGiven = not_given,
        output_format: Optional[Literal["png", "jpeg", "webp"]] | NotGiven = not_given,
        partial_images: Optional[int] | NotGiven = not_given,
        quality: Optional[Literal["standard", "hd", "low", "medium", "high", "auto"]] | NotGiven = not_given,
        response_format: Optional[Literal["url", "b64_json"]] | NotGiven = not_given,
        size: Optional[
            Literal[
                "auto",
                "1024x1024",
                "1536x1024",
                "1024x1536",
                "256x256",
                "512x512",
                "1792x1024",
                "1024x1792",
            ]
        ]
        | NotGiven = not_given,
        stream: Optional[Literal[False]] | Literal[True] | NotGiven = not_given,
        style: Optional[Literal["vivid", "natural"]] | NotGiven = not_given,
        user: str | NotGiven = not_given,
        extra_headers: _openai_images.Headers | None = None,
        extra_query: _openai_images.Query | None = None,
        extra_body: _openai_images.Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ImagesResponse | _openai_images.AsyncStream[_openai_images.ImageGenStreamEvent]:
        response = await super().generate(
            prompt=prompt,
            background=background,
            model=model,
            moderation=moderation,
            n=n,
            output_compression=output_compression,
            output_format=output_format,
            partial_images=partial_images,
            quality=quality,
            response_format=response_format,
            size=size,
            stream=stream,
            style=style,
            user=user,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        )

        return await self._hydrate_b64_json(response, response_format)

    async def _hydrate_b64_json(
        self,
        response: ImagesResponse | _openai_images.AsyncStream[_openai_images.ImageGenStreamEvent],
        response_format: Optional[Literal["url", "b64_json"]] | NotGiven,
    ) -> ImagesResponse | _openai_images.AsyncStream[_openai_images.ImageGenStreamEvent]:
        if response_format != "b64_json" or not isinstance(response, ImagesResponse):
            return response

        images = response.data or []
        missing_b64 = [image for image in images if image.b64_json is None and image.url]
        if not missing_b64:
            return response

        async with httpx.AsyncClient(follow_redirects=True) as client:
            for image in missing_b64:
                assert image.url  # satisfies type checker
                http_response = await client.get(image.url)
                http_response.raise_for_status()
                image.b64_json = base64.b64encode(http_response.content).decode("utf-8")

        return response


__all__ = [name for name in _openai_images.__all__ if name not in {"Images", "AsyncImages"}] + [
    "Images",
    "AsyncImages",
]
