import asyncio

from aimlapi import AsyncAIMLAPI

aimlapi = AsyncAIMLAPI()


# Example: Text to Speech with streaming response
# This will stream mp3 audio file and save it to disk
# Gets AIML_API_KEY from your environment variables

async def main() -> None:
    # Stream mp3 and save to file
    async with aimlapi.audio.speech.with_streaming_response.create(
            model="minimax/speech-2.5-turbo-preview",
            voice="Vince Douglas",
            input="Hello from AI/ML API text to speech!",
            response_format="mp3",
    ) as response:
        with open("tts-output.mp3", "wb") as f:
            async for chunk in response.iter_bytes():
                f.write(chunk)

    print("Saved to tts-output.mp3")


if __name__ == "__main__":
    asyncio.run(main())
