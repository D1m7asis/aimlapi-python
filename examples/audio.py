#!/usr/bin/env rye run python

from pathlib import Path

from aimlapi import AIMLAPI

# gets AIML_API_KEY from your environment variables
aimlapi = AIMLAPI()

speech_file_path = Path(__file__).parent / "speech.mp3"


def main() -> None:
    # Create text-to-speech audio file
    audio = aimlapi.audio.speech.create(
        model="openai/gpt-4o-mini-tts",
        voice="coral",
        input="the quick brown fox jumped over the lazy dogs",
    )
    audio.write_to_file(speech_file_path)

    print(f"Saved to {speech_file_path}")

    # Create transcription from audio file
    transcription = aimlapi.audio.transcriptions.create(
        model="#g1_whisper-small",
        file=speech_file_path,
    )

    print(transcription['result']['results']['channels'][0]['alternatives'][0]['transcript'])

    # AI/ML API's translation endpoint is not yet available

    # Create translation from audio file
    # translation = aimlapi.audio.translations.create(
    #     model="#g1_whisper-small",
    #     file=speech_file_path,
    # )
    # print(translation.text)


if __name__ == "__main__":
    main()
