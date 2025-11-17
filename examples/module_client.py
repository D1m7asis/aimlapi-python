import aimlapi

# will default to `os.environ['AIML_API_KEY']` if not explicitly set
aimlapi.api_key = "..."

# all client options can be configured just like the `OpenAI` instantiation counterpart
aimlapi.base_url = "https://..."
aimlapi.default_headers = {"x-foo": "true"}

# all API calls work in the exact same fashion as well
stream = aimlapi.chat.completions.create(
    model="gpt-4",
    messages=[
        {
            "role": "user",
            "content": "How do I output all files in a directory using Python?",
        },
    ],
    stream=True,
)

for chunk in stream:
    print(chunk.choices[0].delta.content or "", end="", flush=True)

print()
