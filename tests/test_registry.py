"""Реестр событий и README не расходятся с классами."""

import re
from pathlib import Path

import pytest

from conftest import sample_events
from tusumba_contracts import ALL_EVENTS, REGISTRY, BaseEvent, get_event_class, parse_envelope

ROUTING_KEY = re.compile(r"^(?P<producer>[a-z]+)\.[a-z]+(_[a-z]+)*\.[a-z]+$")
README = (Path(__file__).parent.parent / "README.md").read_text(encoding="utf-8")
TABLE_ROW = re.compile(
    r"^\| `(\w+)` \| `([a-z_.]+)` \| ([\w-]+) \| ([^|]+) \| [^|]+ \| (stable|draft) \|$", re.M
)


def service_names(services: tuple[str, ...]) -> str:
    return ", ".join(f"{s}-service" for s in services)


def test_registry() -> None:
    assert len(REGISTRY) == len(ALL_EVENTS)
    assert {type(e) for e in sample_events()} == set(ALL_EVENTS)
    routing_keys = [cls.routing_key for cls in ALL_EVENTS]
    assert len(routing_keys) == len(set(routing_keys))


@pytest.mark.parametrize("cls", ALL_EVENTS, ids=lambda c: c.event_type)
def test_routing_key(cls: type[BaseEvent]) -> None:
    match = ROUTING_KEY.match(cls.routing_key)
    assert match, cls.routing_key
    assert match["producer"] == cls.producer.value


def test_readme_table_matches_classes() -> None:
    rows = TABLE_ROW.findall(README)
    assert [row[0] for row in rows] == [cls.event_type for cls in ALL_EVENTS]
    for event_type, routing_key, producer, consumers, stage in rows:
        cls = get_event_class(event_type, 1)
        assert (routing_key, stage) == (cls.routing_key, cls.stage)
        assert producer == service_names((cls.producer.value,))
        assert consumers.strip() == service_names(tuple(s.value for s in cls.consumers))


def test_readme_json_examples_are_valid() -> None:
    blocks = re.findall(r"```json\n(.*?)```", README, re.S)
    assert blocks
    for block in blocks:
        parse_envelope(block)
