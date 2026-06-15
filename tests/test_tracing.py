from contextlib import nullcontext

from app import tracing


class ClientWithoutPropagation:
    def __init__(self) -> None:
        self.trace_update = None

    def update_current_trace(self, **kwargs) -> None:
        self.trace_update = kwargs


def test_sdk_without_propagate_attributes_is_supported(monkeypatch) -> None:
    client = ClientWithoutPropagation()
    monkeypatch.setattr(tracing, "_client", client)

    context = tracing.trace_context(
        user_id="user-hash",
        session_id="session",
        tags=["lab"],
        metadata={"feature": "qa"},
    )
    assert context is not None
    with context:
        pass

    tracing.update_current_trace(
        user_id="user-hash",
        session_id="session",
        tags=["lab"],
        metadata={"feature": "qa"},
    )
    assert client.trace_update == {
        "name": "chat-request",
        "user_id": "user-hash",
        "session_id": "session",
        "tags": ["lab"],
        "metadata": {"feature": "qa"},
    }
