#!/usr/bin/env -S poetry run python

import asyncio

from aimlapi import AsyncAIMLAPI

# gets API Key from environment variable AIML_API_KEY
client = AsyncAIMLAPI()


async def main() -> None:
    stream = await client.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt="Say this is a test",
        stream=True,
    )
    async for completion in stream:
        print(completion.choices[0].text, end="")
    print()


asyncio.run(main())
