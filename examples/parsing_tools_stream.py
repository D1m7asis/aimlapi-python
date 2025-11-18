from __future__ import annotations

import rich
from pydantic import BaseModel

import aimlapi
from aimlapi import AIMLAPI


class GetWeather(BaseModel):
    city: str
    country: str


client = AIMLAPI()

# TODO: FIX MESSAGES

with client.chat.completions.stream(
    model="gpt-4o-2024-08-06",
    messages=[
        {
            "role": "user",
            "content": "What's the weather like in SF and New York?",
        },
    ],
    tools=[
        # because we're using `.parse_stream()`, the returned tool calls
        # will be automatically deserialized into this `GetWeather` type
        aimlapi.pydantic_function_tool(GetWeather, name="get_weather"),
    ],
    parallel_tool_calls=True,
) as stream:
    for event in stream:
        if event.type == "tool_calls.function.arguments.delta" or event.type == "tool_calls.function.arguments.done":
            rich.get_console().print(event, width=80)

print("----\n")
rich.print(stream.get_final_completion())
