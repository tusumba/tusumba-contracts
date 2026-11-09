"""События Ticketing & Payments. Черновики."""

from typing import ClassVar, Literal, Self
from uuid import UUID

from pydantic import Field, model_validator

from ..base import BaseEvent
from ..types import Money, Service, UtcDatetime


class TicketPurchased(BaseEvent):
    """Черновик (Спринт 3). Покупка оплачена, билеты проданы.

    Notifications отправляет письмо с подтверждением и билетом.
    """

    event_type: ClassVar[str] = "TicketPurchased"
    producer: ClassVar[Service] = Service.TICKETING
    routing_key: ClassVar[str] = "ticketing.ticket.purchased"
    consumers: ClassVar[tuple[Service, ...]] = (Service.NOTIFICATIONS,)

    purchase_id: UUID = Field(description="Покупка (ticketing_db.reservations.id, /v1/purchases/{id})")
    event_id: UUID = Field(description="Мероприятие (events_db.events.id)")
    user_id: UUID = Field(description="Покупатель (identity_db.users.id)")
    ticket_ids: list[UUID] = Field(min_length=1)
    quantity: int = Field(ge=1)
    total: Money
    purchased_at: UtcDatetime

    @model_validator(mode="after")
    def _quantity_matches_tickets(self) -> Self:
        if self.quantity != len(self.ticket_ids):
            raise ValueError("quantity должно совпадать с числом ticket_ids")
        return self


class RegistrationChanged(BaseEvent):
    """Черновик. Запись на мероприятие создана, изменена или снята.

    Notifications создаёт или отменяет напоминание о мероприятии.
    """

    event_type: ClassVar[str] = "RegistrationChanged"
    producer: ClassVar[Service] = Service.TICKETING
    routing_key: ClassVar[str] = "ticketing.registration.changed"
    consumers: ClassVar[tuple[Service, ...]] = (Service.NOTIFICATIONS,)

    registration_id: UUID = Field(description="ticketing_db.registrations.id")
    event_id: UUID = Field(description="Мероприятие (events_db.events.id)")
    user_id: UUID
    action: Literal["created", "updated", "deleted"]
    status: Literal["going", "interested"] | None = Field(
        default=None, description="«Пойду» или «Интересно»; null при action = deleted"
    )
    visibility: Literal["public", "friends_only", "anonymous"] | None = None
    source: Literal["free_signup", "ticket"]

    @model_validator(mode="after")
    def _status_unless_deleted(self) -> Self:
        if self.action != "deleted" and self.status is None:
            raise ValueError("status обязателен, если запись не снята")
        return self
