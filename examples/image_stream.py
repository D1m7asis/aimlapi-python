#!/usr/bin/env python

import base64
from pathlib import Path

from aimlapi import AIMLAPI

client = AIMLAPI()


def _extract_base64(event: object) -> tuple[str | None, int | None]:
    """Return the base64 payload and partial index (if present) for any image event."""

    base64_value = getattr(event, "b64_json", None)
    partial_index = getattr(event, "partial_image_index", None)

    # Response streaming events from the AI/ML API expose partial data under
    # ``partial_image_b64`` and deliver the final image via an
    # ``response.output_item.done`` event with an ``image_generation_call`` item.
    if base64_value is None:
        base64_value = getattr(event, "partial_image_b64", None)

    if base64_value is None and getattr(event, "type", None) == "response.output_item.done":
        item = getattr(event, "item", None)
        if getattr(item, "type", None) == "image_generation_call":
            base64_value = getattr(item, "result", None)

    return base64_value, partial_index


def main() -> None:
    """Example of AIMLAPI image streaming with partial images."""
    stream = client.images.generate(
        model="openai/gpt-image-1",
        prompt="A cute baby sea otter",
        n=1,
        size="1024x1024",
        stream=True,
        partial_images=3,
    )

    for event in stream:
        base64_value, partial_index = _extract_base64(event)

        if getattr(event, "type", None) in {
            "image_generation.partial_image",
            "response.image_generation_call.partial_image",
        }:
            index = (partial_index or 0) + 1
            print(f"  Partial image {index}/3 received")
            print(f"   Size: {len(base64_value or '')} characters (base64)")

            # Save partial image to file
            filename = f"partial_{index}.png"
            image_data = base64.b64decode(base64_value or "")
            with open(filename, "wb") as f:
                f.write(image_data)
            print(f"   💾 Saved to: {Path(filename).resolve()}")

        elif getattr(event, "type", None) in {
            "image_generation.completed",
            "response.output_item.done",
        } and base64_value:
            print(f"\n✅ Final image completed!")
            print(f"   Size: {len(base64_value)} characters (base64)")

            # Save final image to file
            filename = "final_image.png"
            image_data = base64.b64decode(base64_value)
            with open(filename, "wb") as f:
                f.write(image_data)
            print(f"   💾 Saved to: {Path(filename).resolve()}")

        else:
            print(f"❓ Unknown event: {event}")  # type: ignore[unreachable]


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"Error generating image: {error}")
