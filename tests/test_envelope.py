"""Обёртка и разбор сообщений: на этом держатся правила совместимости и повторов."""

import datetime as dt
import json
from typing import Any

import pytest
from pydantic import ValidationError

from conftest import U1, U2, U3
from tusumba_contracts import BaseEvent, FriendRequested, UnknownEventError, parse_envelope


def friend_requested_message() -> dict[str, Any]:
    event = FriendRequested(friend_request_id=U1, from_user_id=U2, to_user_id=U3)
    data: dict[str, Any] = json.loads(event.envelope().model_dump_json())
    return data


def test_round_trip(any_event: BaseEvent) -> None:
    envelope = any_event.envelope()
    parsed = parse_envelope(envelope.model_dump_json())
    assert parsed == envelope
    assert type(parsed.payload) is type(any_event)


def test_unknown_fields_ignored() -> None:
    data = friend_requested_message()
    data["trace_id"] = "abc"
    data["payload"]["new_optional_field"] = 42
    assert isinstance(parse_envelope(data).payload, FriendRequested)


@pytest.mark.parametrize(("field", "value"), [("event_type", "SomethingHappened"), ("version", 99)])
def test_unknown_event_rejected(field: str, value: object) -> None:
    data = friend_requested_message() | {field: value}
    with pytest.raises(UnknownEventError):
        parse_envelope(data)


def test_header_must_match_payload_class() -> None:
    data = friend_requested_message() | {"producer": "events"}
    with pytest.raises(ValidationError, match="не соответствует"):
        parse_envelope(data)


def test_occurred_at_is_utc() -> None:
    event = FriendRequested(friend_request_id=U1, from_user_id=U2, to_user_id=U3)
    novosibirsk = dt.timezone(dt.timedelta(hours=7))
    envelope = event.envelope(occurred_at=dt.datetime(2026, 11, 10, 15, 0, tzinfo=novosibirsk))
    assert envelope.occurred_at == dt.datetime(2026, 11, 10, 8, 0, tzinfo=dt.UTC)
    assert envelope.occurred_at.utcoffset() == dt.timedelta(0)
    with pytest.raises(ValidationError):
        event.envelope(occurred_at=dt.datetime(2026, 11, 10, 8, 0))
