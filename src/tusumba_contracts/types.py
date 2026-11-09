"""Общие типы событий."""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import AfterValidator, AwareDatetime, BaseModel, ConfigDict, Field


class Service(StrEnum):
    """Сервисы Tusumba. Значение - поле `producer` и первая часть routing key."""

    IDENTITY = "identity"
    EVENTS = "events"
    TICKETING = "ticketing"
    MODERATION = "moderation"
    NOTIFICATIONS = "notifications"


def _to_utc(value: datetime) -> datetime:
    return value.astimezone(UTC)


UtcDatetime = Annotated[AwareDatetime, AfterValidator(_to_utc)]
"""Время с часовым поясом, приводится к UTC. Время без пояса - ошибка валидации."""


class ContractModel(BaseModel):
    """База всех моделей пакета: неизменяемые, неизвестные поля игнорируются.

    Игнорирование неизвестных полей нужно для совместимости: отправитель может добавить
    необязательное поле, и старый получатель его просто не заметит.
    """

    model_config = ConfigDict(extra="ignore", frozen=True)


class Money(ContractModel):
    """Сумма в копейках, как в API Ticketing & Payments и Events & Clubs."""

    amount: int = Field(ge=0, description="Сумма в минимальных единицах валюты (копейках)")
    currency: Literal["RUB"] = "RUB"


EventStatus = Literal["not_confirmed", "confirmed", "held", "not_held"]
"""Статус подтверждения мероприятия (events_db.events.status)."""

TeamRole = Literal["owner", "admin", "editor", "scanner"]
"""Роль в команде мероприятия (events_db.event_team_members.role)."""

ApplicationType = Literal["event", "club_page"]
"""Тип заявки (moderation_db.applications.type)."""
