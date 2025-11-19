from __future__ import annotations

import time
from typing import Any, Callable, Collection, Mapping, Protocol

from typing_extensions import runtime_checkable

from openai._base_client import make_request_options
from openai._types import NotGiven, Timeout, not_given

__all__ = ["poll_job", "async_poll_job"]

_DEFAULT_PENDING_STATUSES = frozenset({"waiting", "active", "processing", "queued", "generating"})


StatusCallback = Callable[[Mapping[str, Any]], None]


@runtime_checkable
class _SyncPollingResource(Protocol):
    _get: Any

    def _sleep(self, seconds: float) -> None: ...


@runtime_checkable
class _AsyncPollingResource(Protocol):
    _get: Any

    async def _sleep(self, seconds: float) -> None: ...


def _coerce_timeout(value: float | Timeout | None | NotGiven) -> float | Timeout | None | NotGiven:
    return value if not isinstance(value, NotGiven) else not_given


def _should_keep_waiting(payload: object, pending_statuses: Collection[str]) -> bool:
    if not isinstance(payload, Mapping):
        return False

    status = payload.get("status")
    if isinstance(status, str):
        return status.lower() in pending_statuses

    return False


def poll_job(
    resource: _SyncPollingResource,
    *,
    path_template: str,
    generation_id: str,
    poll_interval: float,
    poll_timeout: float | None,
    request_timeout: float | Timeout | None | NotGiven = not_given,
    status_callback: StatusCallback | None = None,
    pending_statuses: Collection[str] | None = None,
) -> object:
    deadline = None if poll_timeout is None else time.monotonic() + poll_timeout

    if poll_interval <= 0:
        raise ValueError("poll_interval must be greater than 0")

    timeout = _coerce_timeout(request_timeout)
    statuses = (
        _DEFAULT_PENDING_STATUSES
        if pending_statuses is None
        else frozenset(status.lower() for status in pending_statuses)
    )

    while True:
        result = resource._get(  # type: ignore[attr-defined]
            path_template.format(generation_id=generation_id),
            options=make_request_options(timeout=timeout),
            cast_to=object,
        )

        if status_callback is not None and isinstance(result, Mapping):
            status_callback(result)

        if not _should_keep_waiting(result, statuses):
            return result

        if deadline is not None and time.monotonic() >= deadline:
            raise TimeoutError(f"Timed out while waiting for job {generation_id!r} to finish")

        resource._sleep(poll_interval)


async def async_poll_job(
    resource: _AsyncPollingResource,
    *,
    path_template: str,
    generation_id: str,
    poll_interval: float,
    poll_timeout: float | None,
    request_timeout: float | Timeout | None | NotGiven = not_given,
    status_callback: StatusCallback | None = None,
    pending_statuses: Collection[str] | None = None,
) -> object:
    deadline = None if poll_timeout is None else time.monotonic() + poll_timeout

    if poll_interval <= 0:
        raise ValueError("poll_interval must be greater than 0")

    timeout = _coerce_timeout(request_timeout)
    statuses = (
        _DEFAULT_PENDING_STATUSES
        if pending_statuses is None
        else frozenset(status.lower() for status in pending_statuses)
    )

    while True:
        result = await resource._get(  # type: ignore[attr-defined]
            path_template.format(generation_id=generation_id),
            options=make_request_options(timeout=timeout),
            cast_to=object,
        )

        if status_callback is not None and isinstance(result, Mapping):
            status_callback(result)

        if not _should_keep_waiting(result, statuses):
            return result

        if deadline is not None and time.monotonic() >= deadline:
            raise TimeoutError(f"Timed out while waiting for job {generation_id!r} to finish")

        await resource._sleep(poll_interval)
