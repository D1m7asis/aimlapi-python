#!/usr/bin/env -S poetry run python

"""Simple example of the AIMLAPI two-step video generation workflow."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Mapping

import httpx

from aimlapi import OpenAI

OUTPUT_FILE = Path("aimlapi_video.mp4")


def print_status(update: Mapping[str, object]) -> None:
    generation_id = update.get("generation_id") or update.get("id")
    status = update.get("status")
    if generation_id and status:
        print(f"[status] {generation_id}: {status}")
    elif status:
        print(f"[status] {status}")


def download_video(url: str, destination: Path) -> None:
    print(f"Downloading video to {destination}...")
    with httpx.Client(follow_redirects=True, timeout=None) as http:
        with http.stream("GET", url) as response:
            response.raise_for_status()
            with destination.open("wb") as file:
                for chunk in response.iter_bytes():
                    file.write(chunk)
    print(f"Saved video to {destination.resolve()}")


def main() -> None:
    client = OpenAI()

    print("Creating video generation task...")
    try:
        result = client.videos.generate_with_polling(
            model="openai/sora-2-t2v",
            prompt="Cinematic drone footage of bioluminescent waves crashing at sunset",
            duration=6,
            aspect_ratio="16:9",
            status_callback=print_status,
        )
    except TimeoutError as exc:  # pragma: no cover - demo helper
        print(f"Video generation timed out: {exc}")
        sys.exit(1)
    except Exception as exc:  # pragma: no cover - demo helper
        print(f"Failed to start video generation: {exc}")
        sys.exit(1)

    generation_id = result.get("generation_id") or result.get("id")
    status = result.get("status")
    print(f"Final status for {generation_id}: {status}")

    if status == "completed":
        video = result.get("video") or {}
        video_url = video.get("url") if isinstance(video, Mapping) else None
        if video_url:
            print(f"Video URL: {video_url}")
            download_video(video_url, OUTPUT_FILE)
        else:
            print("The API reported completion but did not include a video URL.")
    else:
        error_message = result.get("error")
        print(f"Video generation failed: {error_message or 'Unknown error'}")


if __name__ == "__main__":
    main()
