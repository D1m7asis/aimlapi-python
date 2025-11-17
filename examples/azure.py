from aimlapi import AzureAIMLAPI

# may change in the future
# https://learn.microsoft.com/en-us/azure/ai-services/aimlapi/reference#rest-api-versioning
api_version = "2023-07-01-preview"

# gets the API Key from environment variable AZURE_AIML_API_KEY
client = AzureAIMLAPI(
    api_version=api_version,
    # https://learn.microsoft.com/en-us/azure/cognitive-services/aimlapi/how-to/create-resource?pivots=web-portal#create-a-resource
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
    # https://learn.microsoft.com/en-us/azure/cognitive-services/aimlapi/how-to/create-resource?pivots=web-portal#create-a-resource
    # Navigate to the Azure OpenAI Studio to deploy a model.
    azure_deployment="google/gemini-2.5-pro",  # e.g. gpt-35-instant
)

completion = deployment_client.chat.completions.create(
    model="gpt-5.1-chat-latest",
    messages=[
        {
            "role": "user",
            "content": "How do I output all files in a directory using Python?",
        },
    ],
)
print(completion.to_json())
