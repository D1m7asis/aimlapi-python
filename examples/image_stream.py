#!/usr/bin/env python

import json

from aimlapi import AIMLAPI

client = AIMLAPI()


def main() -> None:
    """Example of AI/ML API image streaming with partial images."""
    with client.images.generate(
            model="openai/gpt-image-1",
            prompt="A cute baby sea otter",
            n=1,
            size="1024x1024",
            stream=True,
            partial_images=3,
    ) as stream:
        body = b""
        for chunk in stream.response.stream:
            body += chunk

        data = json.loads(body.decode("utf-8"))
        created = data["created"]
        url = data["data"][0]["url"]
        print(created, url)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"Error generating image: {error}")
