import asyncio

from aimlapi import AzureAIMLAPI, AsyncAzureAIMLAPI

scopes = "https://cognitiveservices.azure.com/.default"

api_version = "2023-07-01-preview"  # ignore this value; any supported version will work
deployment_name = "gpt-4o"  # set the model name (e.g., "gpt-4o", "gpt-3.5-turbo", etc.)


def sync_main() -> None:
    client = AzureAIMLAPI(
        api_version=api_version,
    )

    completion = client.chat.completions.create(
        model=deployment_name,
        messages=[
            {
                "role": "user",
                "content": "How do I output all files in a directory using Python?",
            }
        ],
    )

    print(completion.to_json())


async def async_main() -> None:
    client = AsyncAzureAIMLAPI(
        api_version=api_version,
    )

    completion = await client.chat.completions.create(
        model=deployment_name,
        messages=[
            {
                "role": "user",
                "content": "How do I output all files in a directory using Python?",
            }
        ],
    )

    print(completion.to_json())


sync_main()

asyncio.run(async_main())
