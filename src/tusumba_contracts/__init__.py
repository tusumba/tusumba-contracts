"""Схемы событий RabbitMQ для сервисов Tusumba."""

from .base import BaseEvent, EventEnvelope
from .events import (
    ApplicationApproved,
    ApplicationRejected,
    ClubPageApplicationData,
    ComplaintResolved,
    EventApplicationData,
    EventInvitationSent,
    EventPublished,
    EventUpdated,
    FriendRequested,
    RegistrationChanged,
    TeamInvitationSent,
    TicketPurchased,
)
from .registry import (
    ALL_EVENTS,
    EXCHANGE,
    EXCHANGE_TYPE,
    REGISTRY,
    UnknownEventError,
    get_event_class,
    parse_envelope,
    queue_name,
)
from .types import Money, Service

__all__ = [
    "ALL_EVENTS",
    "EXCHANGE",
    "EXCHANGE_TYPE",
    "REGISTRY",
    "ApplicationApproved",
    "ApplicationRejected",
    "BaseEvent",
    "ClubPageApplicationData",
    "ComplaintResolved",
    "EventApplicationData",
    "EventEnvelope",
    "EventInvitationSent",
    "EventPublished",
    "EventUpdated",
    "FriendRequested",
    "Money",
    "RegistrationChanged",
    "Service",
    "TeamInvitationSent",
    "TicketPurchased",
    "UnknownEventError",
    "get_event_class",
    "parse_envelope",
    "queue_name",
]
