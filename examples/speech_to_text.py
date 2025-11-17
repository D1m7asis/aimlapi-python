#!/usr/bin/env rye run python

import asyncio

from aimlapi import AsyncAIMLAPI
from openai.helpers import Microphone

# gets AIML_API_KEY from your environment variables
aimlapi = AsyncAIMLAPI()


async def main() -> None:
    print("Recording for the next 10 seconds...")
    recording = await Microphone(timeout=10).record()
    print("Recording complete")

    result = await aimlapi.audio.transcriptions.create(
        model="#g1_whisper-large",  # наш STT-модельный ID
        file=recording,  # bytes-like объект из Microphone
    )

    transcript = (
        result.get("result", {})
        .get("results", {})
        .get("channels", [{}])[0]
        .get("alternatives", [{}])[0]
        .get("transcript")
    )

    if transcript:
        print("Transcription:")
        print(transcript)
    else:
        print("Full STT response:", result)


if __name__ == "__main__":
    asyncio.run(main())
