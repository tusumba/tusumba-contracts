"""События Identity & Social. Черновики."""

from typing import ClassVar
from uuid import UUID

from pydantic import Field

from ..base import BaseEvent
from ..types import Service


class FriendRequested(BaseEvent):
    """Черновик. Отправлен запрос в друзья (#18117). Notifications отправляет push адресату."""

    event_type: ClassVar[str] = "FriendRequested"
    producer: ClassVar[Service] = Service.IDENTITY
    routing_key: ClassVar[str] = "identity.friend_request.created"
    consumers: ClassVar[tuple[Service, ...]] = (Service.NOTIFICATIONS,)

    friend_request_id: UUID = Field(description="identity_db.friend_requests.id")
    from_user_id: UUID
    to_user_id: UUID


class EventInvitationSent(BaseEvent):
    """Черновик. Друг приглашён на мероприятие (#18118). Notifications отправляет push другу."""

    event_type: ClassVar[str] = "EventInvitationSent"
    producer: ClassVar[Service] = Service.IDENTITY
    routing_key: ClassVar[str] = "identity.event_invitation.sent"
    consumers: ClassVar[tuple[Service, ...]] = (Service.NOTIFICATIONS,)

    invitation_id: UUID = Field(description="identity_db.event_invitations.id")
    event_id: UUID = Field(description="Мероприятие (events_db.events.id)")
    from_user_id: UUID
    to_user_id: UUID
