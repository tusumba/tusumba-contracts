"""Реестр событий, константы брокера и разбор входящих сообщений."""

import json
from collections.abc import Mapping
from typing import Any, cast

from pydantic import BaseModel, ConfigDict

from .base import BaseEvent, EventEnvelope
from .events import (
    ApplicationApproved,
    ApplicationRejected,
    ComplaintResolved,
    EventInvitationSent,
    EventPublished,
    EventUpdated,
    FriendRequested,
    RegistrationChanged,
    TeamInvitationSent,
    TicketPurchased,
)
from .types import Service

EXCHANGE = "tusumba.events"
"""Единственный exchange событий: durable, тип topic."""
EXCHANGE_TYPE = "topic"

ALL_EVENTS: tuple[type[BaseEvent], ...] = (
    ApplicationApproved,
    ApplicationRejected,
    ComplaintResolved,
    EventPublished,
    EventUpdated,
    TeamInvitationSent,
    TicketPurchased,
    RegistrationChanged,
    FriendRequested,
    EventInvitationSent,
)
"""Все события в порядке таблицы README."""

REGISTRY: dict[tuple[str, int], type[BaseEvent]] = {(e.event_type, e.version): e for e in ALL_EVENTS}


class UnknownEventError(ValueError):
    """Пришло событие, которого нет в реестре этой версии пакета."""


class _Header(BaseModel):
    model_config = ConfigDict(extra="ignore")
    event_type: str
    version: int


def get_event_class(event_type: str, version: int) -> type[BaseEvent]:
    """Класс события по имени и версии схемы."""
    try:
        return REGISTRY[(event_type, version)]
    except KeyError:
        raise UnknownEventError(f"Неизвестное событие {event_type} v{version}") from None


def parse_envelope(message: bytes | str | Mapping[str, Any]) -> EventEnvelope[BaseEvent]:
    """Разобрать входящее сообщение: по `event_type` и `version` выбирается класс payload."""
    data: Any = json.loads(message) if isinstance(message, bytes | str) else message
    header = _Header.model_validate(data)
    event_cls = get_event_class(header.event_type, header.version)
    envelope_cls = cast(Any, EventEnvelope)[event_cls]
    return cast(EventEnvelope[BaseEvent], envelope_cls.model_validate(data))


def queue_name(consumer: Service, purpose: str) -> str:
    """Имя очереди получателя: `<сервис>.<назначение>`, например `notifications.applications`."""
    return f"{consumer.value}.{purpose}"
