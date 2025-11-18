from aimlapi import AzureAIMLAPI

api_version = "2023-07-01-preview"  # ignore this value; any supported version will work

# gets the API Key from environment variable AIML_API_KEY
client = AzureAIMLAPI(
    api_version=api_version,
)

completion = client.chat.completions.create(
    model="google/gemini-2.5-pro",  # e.g. gpt-35-instant
    messages=[
        {
            "role": "user",
            "content": "How do I output all files in a directory using Python?",
        },
    ],
)
print(completion.to_json())

deployment_client = AzureAIMLAPI(
    api_version=api_version,
    azure_deployment="...",  # ignore this value; set the model in the request instead
)

completion = deployment_client.chat.completions.create(
    model="openai/gpt-5-2025-08-07",
    messages=[
        {
            "role": "user",
            "content": "How do I output all files in a directory using Python?",
        },
    ],
)
print(completion.to_json())
