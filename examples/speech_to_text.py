#!/usr/bin/env rye run python

import os
import time
import asyncio

import httpx
from aimlapi import AsyncAIMLAPI
from openai.helpers import Microphone

# gets AIML_API_KEY from your environment variables
aimlapi = AsyncAIMLAPI()
AIML_API_KEY = os.environ.get("AIML_API_KEY")
BASE_URL = "https://api.aimlapi.com/v1"


async def fetch_stt_result(generation_id: str, timeout: int = 600, interval: int = 10) -> dict:
    """Poll /stt/{generation_id} until готово или timeout."""
    headers = {"Authorization": f"Bearer {AIML_API_KEY}"}
    start = time.time()

    async with httpx.AsyncClient(base_url=BASE_URL, headers=headers, timeout=timeout) as client:
        while time.time() - start < timeout:
            resp = await client.get(f"/stt/{generation_id}")
            resp.raise_for_status()
            data = resp.json()

            status = data.get("status")
            if status in ("waiting", "active"):
                print("Still processing... checking again in", interval, "seconds")
                await asyncio.sleep(interval)
                continue

            return data

    raise TimeoutError("STT processing timeout reached")


async def main() -> None:
    print("Recording for the next 10 seconds...")
    recording = await Microphone(timeout=10).record()
    print("Recording complete")

    # 1. Создаём задачу STT через новый endpoint /stt/create
    task = await aimlapi.audio.transcriptions.create(
        model="#g1_whisper-large",  # наш STT-модельный ID
        file=recording,             # bytes-like объект из Microphone
    )

    generation_id = task.get("generation_id")
    if not generation_id:
        print("No generation_id in response:", task)
        return

    print("STT task created, generation_id:", generation_id)

    # 2. Поллим /stt/{generation_id} пока не будет готов результат
    result = await fetch_stt_result(generation_id)

    # 3. Достаём текст транскрипта из структуры ответа
    try:
        transcript = result["result"]["results"]["channels"][0]["alternatives"][0]["transcript"]
    except Exception:
        print("Full STT response:", result)
        raise

    print("Transcription:")
    print(transcript)


if __name__ == "__main__":
    asyncio.run(main())
