from __future__ import annotations

import copy
import json
from typing import Iterable, Tuple

ResponseEvent = Tuple[str, dict]


def response_payload(text: str = "") -> dict:
    payload = {
        "id": "resp_123",
        "object": "response",
        "created_at": 0,
        "model": "gpt-4o-mini",
        "parallel_tool_calls": True,
        "tool_choice": "auto",
        "tools": [],
        "status": "completed",
        "output": [
            {
                "id": "msg_1",
                "type": "message",
                "role": "assistant",
                "status": "completed",
                "content": [
                    {
                        "type": "output_text",
                        "text": text,
                        "annotations": [],
                        "logprobs": [],
                    }
                ],
            }
        ],
        "temperature": 1.0,
        "top_p": 1.0,
        "background": False,
        "metadata": {},
        "prompt_cache_key": None,
        "safety_identifier": None,
        "service_tier": "default",
        "truncation": "disabled",
        "text": {"format": {"type": "text"}, "verbosity": "medium"},
        "usage": {
            "input_tokens": 1,
            "input_tokens_details": {"cached_tokens": 0},
            "output_tokens": 1,
            "output_tokens_details": {"reasoning_tokens": 0},
            "total_tokens": 2,
        },
    }
    return copy.deepcopy(payload)


def function_response_payload(arguments: str) -> dict:
    payload = response_payload()
    payload["output"] = [
        {
            "id": "call_1",
            "type": "function_call",
            "status": "completed",
            "call_id": "call_1",
            "name": "lookup_city",
            "arguments": arguments,
        }
    ]
    return payload


def sse_bytes(events: Iterable[ResponseEvent]) -> bytes:
    chunks = []
    for name, data in events:
        chunks.append(f"event: {name}\n")
        chunks.append(f"data: {json.dumps(data)}\n\n")
    return "".join(chunks).encode()
