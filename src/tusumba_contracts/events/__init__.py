"""Модели событий по сервисам-отправителям."""

from .events_clubs import EventPublished, EventUpdated, TeamInvitationSent
from .identity import EventInvitationSent, FriendRequested
from .moderation import (
    ApplicationApproved,
    ApplicationRejected,
    ClubPageApplicationData,
    ComplaintResolved,
    EventApplicationData,
)
from .ticketing import RegistrationChanged, TicketPurchased

__all__ = [
    "ApplicationApproved",
    "ApplicationRejected",
    "ClubPageApplicationData",
    "ComplaintResolved",
    "EventApplicationData",
    "EventInvitationSent",
    "EventPublished",
    "EventUpdated",
    "FriendRequested",
    "RegistrationChanged",
    "TeamInvitationSent",
    "TicketPurchased",
]
