#!/usr/bin/env -S poetry run python

"""Simple example of the AIMLAPI two-step video generation workflow."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Mapping

from aimlapi import AIMLAPI

try:
    import httpx
except ImportError:  # pragma: no cover - optional dependency for demo download
    httpx = None

OUTPUT_FILE_URL = Path("aimlapi_video_from_url.mp4")
OUTPUT_FILE_BYTES = Path("aimlapi_video_from_bytes.mp4")


def print_status(update: Mapping[str, object]) -> None:
    generation_id = update.get("generation_id") or update.get("id")
    status = update.get("status")
    if generation_id and status:
        print(f"[status] {generation_id}: {status}")
    elif status:
        print(f"[status] {status}")


def download_video(url: str, destination: Path) -> None:
    print(f"Downloading video to {destination}...")
    if httpx is None:
        raise RuntimeError("httpx is required to download the video from the URL example.")
    with httpx.Client(follow_redirects=True, timeout=None) as http:
        with http.stream("GET", url) as response:
            response.raise_for_status()
            with destination.open("wb") as file:
                for chunk in response.iter_bytes():
                    file.write(chunk)
    print(f"Saved video to {destination.resolve()}")


def generate_json_result(client: AIMLAPI) -> Mapping[str, object]:
    print("Creating video generation task (JSON response)...")
    try:
        result = client.videos.generate_with_polling(
            model="google/veo-3.0-fast",
            prompt="Cinematic drone footage of bioluminescent waves crashing at sunset",
            duration=6,
            aspect_ratio="16:9",
            status_callback=print_status,
            return_bytes=False,
        )
    except TimeoutError as exc:  # pragma: no cover - demo helper
        print(f"Video generation timed out: {exc}")
        sys.exit(1)
    except Exception as exc:  # pragma: no cover - demo helper
        print(f"Failed to start video generation: {exc}")
        sys.exit(1)

    if not isinstance(result, Mapping):
        raise RuntimeError("Expected a JSON mapping when return_bytes=False")

    generation_id = result.get("generation_id") or result.get("id")
    status = result.get("status")
    print(f"Final status for {generation_id}: {status}")
    return result


def generate_video_bytes(client: AIMLAPI) -> bytes:
    print("Creating video generation task (bytes response)...")
    try:
        return client.videos.generate_with_polling(
            model="google/veo-3.0-fast",
            prompt="Cinematic drone footage of a neon-lit city at night",
            duration=4,
            aspect_ratio="9:16",
            status_callback=print_status,
            return_bytes=True,
        )
    except TimeoutError as exc:  # pragma: no cover - demo helper
        print(f"Video generation timed out: {exc}")
        sys.exit(1)
    except Exception as exc:  # pragma: no cover - demo helper
        print(f"Failed to start video generation: {exc}")
        sys.exit(1)


def main() -> None:
    client = AIMLAPI()

    # Example 1: Retrieve the JSON payload (contains the video URL) and download the file manually.
    json_result = generate_json_result(client)
    status = json_result.get("status")
    if status == "completed":
        video = json_result.get("video") or {}
        video_url = video.get("url") if isinstance(video, Mapping) else None
        if video_url:
            print(f"Video URL: {video_url}")
            download_video(video_url, OUTPUT_FILE_URL)
        else:
            print("The API reported completion but did not include a video URL.")
    else:
        error_message = json_result.get("error")
        print(f"Video generation failed: {error_message or 'Unknown error'}")

    # Example 2: Download the final video bytes directly from the helper.
    video_bytes = generate_video_bytes(client)
    OUTPUT_FILE_BYTES.write_bytes(video_bytes)
    print(f"Saved direct video bytes to {OUTPUT_FILE_BYTES.resolve()}")


if __name__ == "__main__":
    main()
