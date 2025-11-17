#!/usr/bin/env python

from aimlapi import AIMLAPI

# gets AIML_API_KEY from your environment variables
aimlapi = AIMLAPI()

prompt = "An astronaut lounging in a tropical resort in space, pixel art"
model = "dall-e-3"


def main() -> None:
    # Generate an image based on the prompt
    response = aimlapi.images.generate(prompt=prompt, model=model)

    # Prints response containing a URL link to image
    print(response)


if __name__ == "__main__":
    main()
