"""События Events & Clubs. Черновики, поля сверены с OpenAPI Events & Clubs (#18891)."""

import datetime as dt
from typing import ClassVar, Literal, Self
from uuid import UUID

from pydantic import Field, model_validator

from ..base import BaseEvent
from ..types import EventStatus, Money, Service, TeamRole

EditableEventField = Literal["title", "description", "date", "place_address", "is_free", "price", "status"]
"""Поля мероприятия, которые меняет `PATCH /v1/events/{id}` (схема `EventUpdate`)."""


class EventPublished(BaseEvent):
    """Черновик. Мероприятие создано по одобренной заявке и опубликовано.

    Поля - как в `EventInternal` Events & Clubs (`id` здесь - `event_id`).
    Получатель по компонентной диаграмме - Notifications; кого она уведомляет, не определено.
    """

    event_type: ClassVar[str] = "EventPublished"
    producer: ClassVar[Service] = Service.EVENTS
    routing_key: ClassVar[str] = "events.event.published"
    consumers: ClassVar[tuple[Service, ...]] = (Service.NOTIFICATIONS,)

    event_id: UUID = Field(description="events_db.events.id")
    current_version_id: UUID
    title: str
    date: dt.date
    place_address: str
    is_free: bool
    price: Money | None = None
    status: EventStatus
    club_id: UUID | None = None
    created_by_user_id: UUID


class EventUpdated(BaseEvent):
    """Черновик. Мероприятие отредактировано (`PATCH /v1/events/{id}`).

    Поля мероприятия - состояние после изменения; `changed_fields` - что изменилось.
    Notifications переносит напоминания при смене даты.
    """

    event_type: ClassVar[str] = "EventUpdated"
    producer: ClassVar[Service] = Service.EVENTS
    routing_key: ClassVar[str] = "events.event.updated"
    consumers: ClassVar[tuple[Service, ...]] = (Service.NOTIFICATIONS,)

    event_id: UUID = Field(description="events_db.events.id")
    current_version_id: UUID
    title: str
    date: dt.date
    place_address: str
    is_free: bool
    price: Money | None = None
    status: EventStatus
    club_id: UUID | None = None
    edited_by: UUID
    changed_fields: list[EditableEventField] = Field(
        min_length=1, description="Изменённые поля - из тех, что принимает PATCH /v1/events/{id}"
    )


class TeamInvitationSent(BaseEvent):
    """Черновик. Пользователь приглашён в команду мероприятия.

    Поля - как в `TeamInvitation` Events & Clubs (`id` здесь - `invitation_id`), кроме `status`:
    при отправке приглашение всегда ждёт ответа. Notifications отправляет push зарегистрированному
    пользователю или письмо на `invitee_email`. Указывается ровно одно из полей `invitee_user_id`
    и `invitee_email`.
    """

    event_type: ClassVar[str] = "TeamInvitationSent"
    producer: ClassVar[Service] = Service.EVENTS
    routing_key: ClassVar[str] = "events.team_invitation.sent"
    consumers: ClassVar[tuple[Service, ...]] = (Service.NOTIFICATIONS,)

    invitation_id: UUID = Field(description="events_db.team_invitations.id")
    event_id: UUID
    event_title: str
    invitee_user_id: UUID | None = None
    invitee_email: str | None = Field(default=None, max_length=254, pattern=r"^[^@\s]+@[^@\s]+$")
    role: TeamRole
    invited_by: UUID

    @model_validator(mode="after")
    def _exactly_one_invitee(self) -> Self:
        if (self.invitee_user_id is None) == (self.invitee_email is None):
            raise ValueError("Нужно указать ровно одно из полей invitee_user_id и invitee_email")
        return self
