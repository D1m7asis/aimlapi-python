# AI/ML API Python SDK (OpenAI compatible)

AI/ML API provides access to 300+ AI models (including DeepSeek, Gemini, and ChatGPT) with enterprise-grade rate limits and uptime. This package is an OpenAI-compatible fork of the official OpenAI Python client and defaults to the AI/ML API endpoints so you can reuse familiar APIs while targeting [api.aimlapi.com](https://api.aimlapi.com/v1/).

- Models: https://aimlapi.com/models
- REST API reference: https://docs.aimlapi.com/
- Example endpoints: https://api.aimlapi.com/v1/ and https://api.aimlapi.com/v1/chat/completions

The full typed surface area of the SDK is documented in [api.md](api.md).

## Installation

```sh
pip install aimlapi
```

## Quickstart

The SDK exposes OpenAI-compatible sync and async clients while applying AI/ML defaults such as the base URL and header metadata. By default the client picks up your `AIML_API_KEY` (or `AIMLAPI_API_KEY`) environment variable and targets `https://api.aimlapi.com/v1`.

```python
import os
from aimlapi import AIMLAPI

client = AIMLAPI(
    api_key=os.environ.get("AIML_API_KEY"),
)

completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "developer", "content": "Talk like a pirate."},
        {"role": "user", "content": "How do I check if a Python object is an instance of a class?"},
    ],
)

print(completion.choices[0].message.content)
```

You can also use the streaming-friendly [Responses API](https://docs.aimlapi.com/api-reference/responses) with the same interface:

```python
from aimlapi import AIMLAPI

client = AIMLAPI()

response = client.responses.create(
    model="gpt-4o",
    instructions="You are a coding assistant that talks like a pirate.",
    input="How do I check if a Python object is an instance of a class?",
)

print(response.output_text)
```

> **Note:** The remaining sections mirror the upstream OpenAI README for advanced scenarios. Replace `openai` imports with `aimlapi` to reuse the same APIs against the AI/ML API service.

### Vision

With an image URL:

```python
prompt = "What is in this image?"
img_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/2023_06_08_Raccoon1.jpg/1599px-2023_06_08_Raccoon1.jpg"

response = client.responses.create(
    model="gpt-4o-mini",
    input=[
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": prompt},
                {"type": "input_image", "image_url": f"{img_url}"},
            ],
        }
    ],
)
```

With the image as a base64 encoded string:

```python
import base64
from aimlapi import AIMLAPI

client = AIMLAPI()

prompt = "What is in this image?"
with open("path/to/image.png", "rb") as image_file:
    b64_image = base64.b64encode(image_file.read()).decode("utf-8")

response = client.responses.create(
    model="gpt-4o-mini",
    input=[
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": prompt},
                {"type": "input_image", "image_url": f"data:image/png;base64,{b64_image}"},
            ],
        }
    ],
)
```

## Async usage

Simply import `AsyncAIMLAPI` instead of `AIMLAPI` and use `await` with each API call:

```python
import os
import asyncio
from aimlapi import AsyncAIMLAPI

client = AsyncAIMLAPI(
    # This is the default and can be omitted
    api_key=os.environ.get("AIML_API_KEY"),
)


async def main() -> None:
    response = await client.responses.create(
        model="gpt-4o", input="Explain disestablishmentarianism to a smart five year old."
    )
    print(response.output_text)


asyncio.run(main())
```

Functionality between the synchronous and asynchronous clients is otherwise identical.

### With aiohttp

By default, the async client uses `httpx` for HTTP requests. However, for improved concurrency performance you may also use `aiohttp` as the HTTP backend.

You can enable this by installing `aiohttp`:

```sh
# install from PyPI
pip install aimlapi[aiohttp]
```

Then you can enable it by instantiating the client with `http_client=DefaultAioHttpClient()`:

```python
import asyncio
from aimlapi import AsyncAIMLAPI, DefaultAioHttpClient


async def main() -> None:
    async with AsyncAIMLAPI(
        api_key="My API Key",
        http_client=DefaultAioHttpClient(),
    ) as client:
        chat_completion = await client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Say this is a test",
                }
            ],
            model="gpt-4o",
        )


asyncio.run(main())
```

## Streaming responses

We provide support for streaming responses using Server Side Events (SSE).

```python
from aimlapi import AIMLAPI

client = AIMLAPI()

stream = client.responses.create(
    model="gpt-4o",
    input="Write a one-sentence bedtime story about a unicorn.",
    stream=True,
)

for event in stream:
    print(event)
```

The async client uses the exact same interface.

```python
import asyncio
from aimlapi import AsyncAIMLAPI

client = AsyncAIMLAPI()


async def main():
    stream = await client.responses.create(
        model="gpt-4o",
        input="Write a one-sentence bedtime story about a unicorn.",
        stream=True,
    )

    async for event in stream:
        print(event)


asyncio.run(main())
```

## Realtime API

The Realtime API enables you to build low-latency, multi-modal conversational experiences. It currently supports text and audio as both input and output, as well as [function calling](https://platform.openai.com/docs/guides/function-calling) through a WebSocket connection.

Under the hood the SDK uses the [`websockets`](https://websockets.readthedocs.io/en/stable/) library to manage connections.

The Realtime API works through a combination of client-sent events and server-sent events. Clients can send events to do things like update session configuration or send text and audio inputs. Server events confirm when audio responses have completed, or when a text response from the model has been received. A full event reference can be found [here](https://platform.openai.com/docs/api-reference/realtime-client-events) and a guide can be found [here](https://platform.openai.com/docs/guides/realtime).

Basic text based example:

```py
import asyncio
from aimlapi import AsyncAIMLAPI

async def main():
    client = AsyncAIMLAPI()

    async with client.realtime.connect(model="gpt-realtime") as connection:
        await connection.session.update(
            session={"type": "realtime", "output_modalities": ["text"]}
        )

        await connection.conversation.item.create(
            item={
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": "Say hello!"}],
            }
        )
        await connection.response.create()

        async for event in connection:
            if event.type == "response.output_text.delta":
                print(event.delta, flush=True, end="")

            elif event.type == "response.output_text.done":
                print()

            elif event.type == "response.done":
                break

asyncio.run(main())
```

However the real magic of the Realtime API is handling audio inputs / outputs, see this example [TUI script](https://github.com/openai/openai-python/blob/main/examples/realtime/push_to_talk_app.py) for a fully fledged example.

### Realtime error handling

Whenever an error occurs, the Realtime API will send an [`error` event](https://platform.openai.com/docs/guides/realtime-model-capabilities#error-handling) and the connection will stay open and remain usable. This means you need to handle it yourself, as _no errors are raised directly_ by the SDK when an `error` event comes in.

```py
client = AsyncAIMLAPI()

async with client.realtime.connect(model="gpt-realtime") as connection:
    ...
    async for event in connection:
        if event.type == 'error':
            print(event.error.type)
            print(event.error.code)
            print(event.error.event_id)
            print(event.error.message)
```

## Using types

Nested request parameters are [TypedDicts](https://docs.python.org/3/library/typing.html#typing.TypedDict). Responses are [Pydantic models](https://docs.pydantic.dev) which also provide helper methods for things like:

- Serializing back into JSON, `model.to_json()`
- Converting to a dictionary, `model.to_dict()`

Typed requests and responses provide autocomplete and documentation within your editor. If you would like to see type errors in VS Code to help catch bugs earlier, set `python.analysis.typeCheckingMode` to `basic`.

## Pagination

List methods in the OpenAI API are paginated.

This library provides auto-paginating iterators with each list response, so you do not have to request successive pages manually:

```python
from aimlapi import AIMLAPI

client = AIMLAPI()

all_jobs = []
# Automatically fetches more pages as needed.
for job in client.fine_tuning.jobs.list(
    limit=20,
):
    # Do something with job here
    all_jobs.append(job)
print(all_jobs)
```

Or, asynchronously:

```python
import asyncio
from aimlapi import AsyncAIMLAPI

client = AsyncAIMLAPI()


async def main() -> None:
    all_jobs = []
    # Iterate through items across all pages, issuing requests as needed.
    async for job in client.fine_tuning.jobs.list(
        limit=20,
    ):
        all_jobs.append(job)
    print(all_jobs)


asyncio.run(main())
```

Alternatively, you can use the `.has_next_page()`, `.next_page_info()`, or `.get_next_page()` methods for more granular control working with pages:

```python
first_page = await client.fine_tuning.jobs.list(
    limit=20,
)
if first_page.has_next_page():
    print(f"will fetch next page using these details: {first_page.next_page_info()}")
    next_page = await first_page.get_next_page()
    print(f"number of items we just fetched: {len(next_page.data)}")

# Remove `await` for non-async usage.
```

Or just work directly with the returned data:

```python
first_page = await client.fine_tuning.jobs.list(
    limit=20,
)

print(f"next page cursor: {first_page.after}")  # => "next page cursor: ..."
for job in first_page.data:
    print(job.id)

# Remove `await` for non-async usage.
```

## Nested params

Nested parameters are dictionaries, typed using `TypedDict`, for example:

```python
from aimlapi import AIMLAPI

client = AIMLAPI()

response = client.chat.responses.create(
    input=[
        {
            "role": "user",
            "content": "How much ?",
        }
    ],
    model="gpt-4o",
    response_format={"type": "json_object"},
)
```

## File uploads

Request parameters that correspond to file uploads can be passed as `bytes`, or a [`PathLike`](https://docs.python.org/3/library/os.html#os.PathLike) instance or a tuple of `(filename, contents, media type)`.

```python
from pathlib import Path
from aimlapi import AIMLAPI

client = AIMLAPI()

client.files.create(
    file=Path("input.jsonl"),
    purpose="fine-tune",
)
```

The async client uses the exact same interface. If you pass a [`PathLike`](https://docs.python.org/3/library/os.html#os.PathLike) instance, the file contents will be read asynchronously automatically.

## Webhook Verification

Verifying webhook signatures is _optional but encouraged_.

For more information about webhooks, see [the API docs](https://platform.openai.com/docs/guides/webhooks).

### Parsing webhook payloads

For most use cases, you will likely want to verify the webhook and parse the payload at the same time. To achieve this, we provide the method `client.webhooks.unwrap()`, which parses a webhook request and verifies that it was sent by the AI/ML API service. This method will raise an error if the signature is invalid.

Note that the `body` parameter must be the raw JSON string sent from the server (do not parse it first). The `.unwrap()` method will parse this JSON for you into an event object after verifying the webhook was sent from AI/ML API.

```python
from aimlapi import AIMLAPI
from flask import Flask, request

app = Flask(__name__)
client = AIMLAPI()


@app.route("/webhook", methods=["POST"])
def webhook():
    request_body = request.get_data(as_text=True)

    try:
        event = client.webhooks.unwrap(request_body, request.headers)

        if event.type == "response.completed":
            print("Response completed:", event.data)
        elif event.type == "response.failed":
            print("Response failed:", event.data)
        else:
            print("Unhandled event type:", event.type)

        return "ok"
    except Exception as e:
        print("Invalid signature:", e)
        return "Invalid signature", 400


if __name__ == "__main__":
    app.run(port=8000)
```

### Verifying webhook payloads directly

In some cases, you may want to verify the webhook separately from parsing the payload. If you prefer to handle these steps separately, we provide the method `client.webhooks.verify_signature()` to _only verify_ the signature of a webhook request. Like `.unwrap()`, this method will raise an error if the signature is invalid.

Note that the `body` parameter must be the raw JSON string sent from the server (do not parse it first). You will then need to parse the body after verifying the signature.

```python
import json
from aimlapi import AIMLAPI
from flask import Flask, request

app = Flask(__name__)
client = AIMLAPI()


@app.route("/webhook", methods=["POST"])
def webhook():
    request_body = request.get_data(as_text=True)

    try:
        client.webhooks.verify_signature(request_body, request.headers)

        # Parse the body after verification
        event = json.loads(request_body)
        print("Verified event:", event)

        return "ok"
    except Exception as e:
        print("Invalid signature:", e)
        return "Invalid signature", 400


if __name__ == "__main__":
    app.run(port=8000)
```

## Handling errors

When the library is unable to connect to the API (for example, due to network connection problems or a timeout), a subclass of `aimlapi.APIConnectionError` is raised.

When the API returns a non-success status code (that is, 4xx or 5xx response), a subclass of `aimlapi.APIStatusError` is raised, containing `status_code` and `response` properties.

All errors inherit from `aimlapi.APIError`.

```python
import aimlapi
from aimlapi import AIMLAPI

client = AIMLAPI()

try:
    client.fine_tuning.jobs.create(
        model="gpt-4o",
        training_file="file-abc123",
    )
except aimlapi.APIConnectionError as e:
    print("The server could not be reached")
    print(e.__cause__)  # an underlying Exception, likely raised within httpx.
except aimlapi.RateLimitError as e:
    print("A 429 status code was received; we should back off a bit.")
except aimlapi.APIStatusError as e:
    print("Another non-200-range status code was received")
    print(e.status_code)
    print(e.response)
```

Error codes are as follows:

| Status Code | Error Type                 |
| ----------- | -------------------------- |
| 400         | `BadRequestError`          |
| 401         | `AuthenticationError`      |
| 403         | `PermissionDeniedError`    |
| 404         | `NotFoundError`            |
| 422         | `UnprocessableEntityError` |
| 429         | `RateLimitError`           |
| >=500       | `InternalServerError`      |
| N/A         | `APIConnectionError`       |

## Request IDs

> For more information on debugging requests, see [these docs](https://platform.openai.com/docs/api-reference/debugging-requests)

All object responses in the SDK provide a `_request_id` property which is added from the `x-request-id` response header so that you can quickly log failing requests and report them back to OpenAI.

```python
response = await client.responses.create(
    model="gpt-4o-mini",
    input="Say 'this is a test'.",
)
print(response._request_id)  # req_123
```

Note that unlike other properties that use an `_` prefix, the `_request_id` property
_is_ public. Unless documented otherwise, _all_ other `_` prefix properties,
methods and modules are _private_.

> [!IMPORTANT]  
> If you need to access request IDs for failed requests you must catch the `APIStatusError` exception

```python
import aimlapi

try:
    completion = await client.chat.completions.create(
        messages=[{"role": "user", "content": "Say this is a test"}], model="gpt-4"
    )
except aimlapi.APIStatusError as exc:
    print(exc.request_id)  # req_123
    raise exc
```

## Retries

Certain errors are automatically retried 2 times by default, with a short exponential backoff.
Connection errors (for example, due to a network connectivity problem), 408 Request Timeout, 409 Conflict,
429 Rate Limit, and >=500 Internal errors are all retried by default.

You can use the `max_retries` option to configure or disable retry settings:

```python
from aimlapi import AIMLAPI

# Configure the default for all requests:
client = AIMLAPI(
    # default is 2
    max_retries=0,
)

# Or, configure per-request:
client.with_options(max_retries=5).chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "How can I get the name of the current day in JavaScript?",
        }
    ],
    model="gpt-4o",
)
```

## Timeouts

By default requests time out after 10 minutes. You can configure this with a `timeout` option,
which accepts a float or an [`httpx.Timeout`](https://www.python-httpx.org/advanced/timeouts/#fine-tuning-the-configuration) object:

```python
from aimlapi import AIMLAPI

# Configure the default for all requests:
client = AIMLAPI(
    # 20 seconds (default is 10 minutes)
    timeout=20.0,
)

# More granular control:
client = AIMLAPI(
    timeout=httpx.Timeout(60.0, read=5.0, write=10.0, connect=2.0),
)

# Override per-request:
client.with_options(timeout=5.0).chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "How can I list all files in a directory using Python?",
        }
    ],
    model="gpt-4o",
)
```

On timeout, an `APITimeoutError` is thrown.

Note that requests that time out are [retried twice by default](#retries).

## Advanced

### Logging

We use the standard library [`logging`](https://docs.python.org/3/library/logging.html) module.

You can enable logging by setting the environment variable `AIMLAPI_LOG` to `info`.

```shell
$ export AIMLAPI_LOG=info
```

Or to `debug` for more verbose logging.

### How to tell whether `None` means `null` or missing

In an API response, a field may be explicitly `null`, or missing entirely; in either case, its value is `None` in this library. You can differentiate the two cases with `.model_fields_set`:

```py
if response.my_field is None:
  if 'my_field' not in response.model_fields_set:
    print('Got json like {}, without a "my_field" key present at all.')
  else:
    print('Got json like {"my_field": null}.')
```

### Accessing raw response data (e.g. headers)

The "raw" Response object can be accessed by prefixing `.with_raw_response.` to any HTTP method call, e.g.,

```py
from aimlapi import AIMLAPI

client = AIMLAPI()
response = client.chat.completions.with_raw_response.create(
    messages=[{
        "role": "user",
        "content": "Say this is a test",
    }],
    model="gpt-4o",
)
print(response.headers.get('X-My-Header'))

completion = response.parse()  # get the object that `chat.completions.create()` would have returned
print(completion)
```

These methods return a [`LegacyAPIResponse`](https://github.com/openai/openai-python/tree/main/src/openai/_legacy_response.py) object. This is a legacy class as we're changing it slightly in the next major version.

For the sync client this will mostly be the same with the exception
of `content` & `text` will be methods instead of properties. In the
async client, all methods will be async.

A migration script will be provided & the migration in general should
be smooth.

#### `.with_streaming_response`

The above interface eagerly reads the full response body when you make the request, which may not always be what you want.

To stream the response body, use `.with_streaming_response` instead, which requires a context manager and only reads the response body once you call `.read()`, `.text()`, `.json()`, `.iter_bytes()`, `.iter_text()`, `.iter_lines()` or `.parse()`. In the async client, these are async methods.

As such, `.with_streaming_response` methods return a different [`APIResponse`](https://github.com/openai/openai-python/tree/main/src/openai/_response.py) object, and the async client returns an [`AsyncAPIResponse`](https://github.com/openai/openai-python/tree/main/src/openai/_response.py) object.

```python
with client.chat.completions.with_streaming_response.create(
    messages=[
        {
            "role": "user",
            "content": "Say this is a test",
        }
    ],
    model="gpt-4o",
) as response:
    print(response.headers.get("X-My-Header"))

    for line in response.iter_lines():
        print(line)
```

The context manager is required so that the response will reliably be closed.

### Making custom/undocumented requests

This library is typed for convenient access to the documented API.

If you need to access undocumented endpoints, params, or response properties, the library can still be used.

#### Undocumented endpoints

To make requests to undocumented endpoints, you can make requests using `client.get`, `client.post`, and other
http verbs. Options on the client will be respected (such as retries) when making this request.

```py
import httpx

response = client.post(
    "/foo",
    cast_to=httpx.Response,
    body={"my_param": True},
)

print(response.headers.get("x-foo"))
```

#### Undocumented request params

If you want to explicitly send an extra param, you can do so with the `extra_query`, `extra_body`, and `extra_headers` request
options.

#### Undocumented response properties

To access undocumented response properties, you can access the extra fields like `response.unknown_prop`. You
can also get all the extra fields on the Pydantic model as a dict with
[`response.model_extra`](https://docs.pydantic.dev/latest/api/base_model/#pydantic.BaseModel.model_extra).

### Configuring the HTTP client

You can directly override the [httpx client](https://www.python-httpx.org/api/#client) to customize it for your use case, including:

- Support for [proxies](https://www.python-httpx.org/advanced/proxies/)
- Custom [transports](https://www.python-httpx.org/advanced/transports/)
- Additional [advanced](https://www.python-httpx.org/advanced/clients/) functionality

```python
import httpx
from aimlapi import AIMLAPI, DefaultHttpxClient

client = AIMLAPI(
    # Or use the `AIML_API_BASE` env var
    base_url="http://my.test.server.example.com:8083/v1",
    http_client=DefaultHttpxClient(
        proxy="http://my.test.proxy.example.com",
        transport=httpx.HTTPTransport(local_address="0.0.0.0"),
    ),
)
```

You can also customize the client on a per-request basis by using `with_options()`:

```python
client.with_options(http_client=DefaultHttpxClient(...))
```

### Managing HTTP resources

By default the library closes underlying HTTP connections whenever the client is [garbage collected](https://docs.python.org/3/reference/datamodel.html#object.__del__). You can manually close the client using the `.close()` method if desired, or with a context manager that closes when exiting.

```py
from aimlapi import AIMLAPI

with AIMLAPI() as client:
  # make requests here
  ...

# HTTP client is now closed
```

## Microsoft Azure

To target Azure-hosted deployments, use the `AzureAIMLAPI` class instead of `AIMLAPI`.

> [!IMPORTANT]
> The Azure API shape differs from the core API shape which means that the static types for responses / params
> won't always be correct.

```py
from aimlapi import AzureAIMLAPI

# gets the API Key from environment variable AIML_API_KEY
client = AzureAIMLAPI(
    # Azure API versions are still required when targeting Azure endpoints
    api_version="2023-07-01-preview",
)

completion = client.chat.completions.create(
    model="deployment-name",  # e.g. gpt-35-instant
    messages=[
        {
            "role": "user",
            "content": "How do I output all files in a directory using Python?",
        },
    ],
)
print(completion.to_json())
```

In addition to the options provided in the base `AIMLAPI` client, the following options are provided:

- `azure_endpoint` (or the `AZURE_AIML_ENDPOINT` environment variable)
- `azure_deployment`
- `api_version` (or the `AIML_API_VERSION` environment variable)
- `azure_ad_token`
- `azure_ad_token_provider`

An example of using the client with Microsoft Entra ID (formerly known as Azure Active Directory) can be found [here](https://github.com/openai/openai-python/blob/main/examples/azure_ad.py).

## Versioning

This package generally follows [SemVer](https://semver.org/spec/v2.0.0.html) conventions, though certain backwards-incompatible changes may be released as minor versions:

1. Changes that only affect static types, without breaking runtime behavior.
2. Changes to library internals which are technically public but not intended or documented for external use. _(Please open a GitHub issue to let us know if you are relying on such internals.)_
3. Changes that we do not expect to impact the vast majority of users in practice.

We take backwards-compatibility seriously and work hard to ensure you can rely on a smooth upgrade experience.

We are keen for your feedback; please open an [issue](https://www.github.com/openai/openai-python/issues) with questions, bugs, or suggestions.

### Determining the installed version

If you've upgraded to the latest version but aren't seeing any new features you were expecting then your python environment is likely still using an older version.

You can determine the version that is being used at runtime with:

```py
import aimlapi
print(aimlapi.__version__)
```

## Requirements

Python 3.9 or higher.

## Contributing

See [the contributing documentation](./CONTRIBUTING.md).
