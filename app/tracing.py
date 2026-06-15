from __future__ import annotations

import importlib.metadata
import os
from contextlib import contextmanager, nullcontext
from typing import Any

from dotenv import load_dotenv

load_dotenv()

SDK_AVAILABLE = False
SDK_API = "unavailable"

try:
    from langfuse import get_client, observe as _langfuse_observe

    SDK_AVAILABLE = True
    SDK_API = "v4"
    _configured = bool(
        os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY")
    )
    _client = get_client() if _configured else None

    def observe(*args: Any, **kwargs: Any):
        if _client is not None:
            return _langfuse_observe(*args, **kwargs)

        def decorator(func):
            return func

        return decorator

    @contextmanager
    def trace_context(
        *,
        user_id: str,
        session_id: str,
        tags: list[str],
        metadata: dict[str, Any],
    ):
        if _client is None:
            yield
            return
        propagate = getattr(_client, "propagate_attributes", None)
        if propagate is None:
            yield
            return
        with propagate(
            user_id=user_id,
            session_id=session_id,
            tags=tags,
            metadata=metadata,
            trace_name="chat-request",
        ):
            yield

    def update_current_observation(
        *,
        metadata: dict[str, Any],
        usage_details: dict[str, int] | None = None,
        cost_details: dict[str, float] | None = None,
        model: str | None = None,
        output: Any = None,
        generation: bool = False,
    ) -> None:
        if _client is None:
            return
        if generation:
            _client.update_current_generation(
                metadata=metadata,
                usage_details=usage_details,
                cost_details=cost_details,
                model=model,
                output=output,
            )
        else:
            _client.update_current_span(metadata=metadata, output=output)

    def current_trace_id() -> str | None:
        return _client.get_current_trace_id() if _client is not None else None

    def flush_traces() -> None:
        if _client is not None:
            _client.flush()

except (ImportError, AttributeError):
    try:
        from langfuse.decorators import langfuse_context as _legacy_context
        from langfuse.decorators import observe

        SDK_AVAILABLE = True
        SDK_API = "legacy"

        def trace_context(
            *,
            user_id: str,
            session_id: str,
            tags: list[str],
            metadata: dict[str, Any],
        ):
            return nullcontext()

        def update_current_trace(
            *,
            user_id: str,
            session_id: str,
            tags: list[str],
            metadata: dict[str, Any],
        ) -> None:
            _legacy_context.update_current_trace(
                user_id=user_id,
                session_id=session_id,
                tags=tags,
                metadata=metadata,
                name="chat-request",
            )

        def update_current_observation(
            *,
            metadata: dict[str, Any],
            usage_details: dict[str, int] | None = None,
            cost_details: dict[str, float] | None = None,
            model: str | None = None,
            output: Any = None,
            generation: bool = False,
        ) -> None:
            _legacy_context.update_current_observation(
                metadata=metadata,
                usage_details=usage_details,
                model=model,
                output=output,
            )

        def current_trace_id() -> str | None:
            return _legacy_context.get_current_trace_id()

        def flush_traces() -> None:
            _legacy_context.flush()

    except ImportError:
        def observe(*args: Any, **kwargs: Any):
            def decorator(func):
                return func

            return decorator

        def trace_context(
            *,
            user_id: str,
            session_id: str,
            tags: list[str],
            metadata: dict[str, Any],
        ):
            return nullcontext()

        def update_current_observation(**kwargs: Any) -> None:
            return None

        def current_trace_id() -> str | None:
            return None

        def flush_traces() -> None:
            return None


if SDK_API == "v4":
    def update_current_trace(
        *,
        user_id: str,
        session_id: str,
        tags: list[str],
        metadata: dict[str, Any],
    ) -> None:
        if _client is None:
            return
        update = getattr(_client, "update_current_trace", None)
        if update is not None:
            update(
                name="chat-request",
                user_id=user_id,
                session_id=session_id,
                tags=tags,
                metadata=metadata,
            )
elif SDK_API != "legacy":
    def update_current_trace(
        *,
        user_id: str,
        session_id: str,
        tags: list[str],
        metadata: dict[str, Any],
    ) -> None:
        return None


def tracing_enabled() -> bool:
    configured = bool(
        os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY")
    )
    if SDK_API == "v4":
        return SDK_AVAILABLE and configured and _client is not None
    return SDK_AVAILABLE and configured


def tracing_status() -> dict[str, Any]:
    try:
        version = importlib.metadata.version("langfuse")
    except importlib.metadata.PackageNotFoundError:
        version = None
    return {
        "configured": tracing_enabled(),
        "sdk_available": SDK_AVAILABLE,
        "sdk_api": SDK_API,
        "sdk_version": version,
        "host": os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
    }
