"""События Moderation. Поля заявки совпадают со схемами OpenAPI Moderation (#18890)."""

import datetime as dt
from typing import ClassVar, Literal, Self
from uuid import UUID

from pydantic import Field, model_validator

from ..base import BaseEvent, Stage
from ..types import ApplicationType, ContractModel, Money, Service, UtcDatetime


class EventApplicationData(ContractModel):
    """Данные заявки на мероприятие (`EventApplicationData` в OpenAPI Moderation)."""

    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1, max_length=1000)
    date: dt.date
    place_address: str = Field(min_length=1, max_length=500)
    is_free: bool
    price: Money | None = Field(default=None, description="Обязательна для платного мероприятия")

    @model_validator(mode="after")
    def _paid_event_has_price(self) -> Self:
        if not self.is_free and self.price is None:
            raise ValueError("У платного мероприятия должна быть цена")
        return self


class ClubPageApplicationData(ContractModel):
    """Данные заявки на страницу секции (`ClubPageApplicationData` в OpenAPI Moderation)."""

    name: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1, max_length=1000)
    meeting_place: str | None = Field(default=None, max_length=500)
    schedule: str | None = Field(default=None, max_length=1000)
    contacts: dict[str, str] = Field(default_factory=dict, description="Ключ - канал связи, значение - адрес")


class ApplicationApproved(BaseEvent):
    """Модератор одобрил заявку на мероприятие или страницу секции.

    Events & Clubs создаёт объект с id `result_object_id`, первую версию текста и назначает
    автора заявки владельцем команды (`event_team_members`, роль `owner`) или администратором
    секции (`club_admins`). Повтор события не должен создавать второй объект.
    Notifications сообщает автору, что заявка одобрена.

    Заполнен блок, соответствующий `type`: `event` или `club_page`, как в заявке Moderation.
    """

    event_type: ClassVar[str] = "ApplicationApproved"
    producer: ClassVar[Service] = Service.MODERATION
    routing_key: ClassVar[str] = "moderation.application.approved"
    consumers: ClassVar[tuple[Service, ...]] = (Service.EVENTS, Service.NOTIFICATIONS)
    stage: ClassVar[Stage] = "stable"

    application_id: UUID = Field(description="moderation_db.applications.id")
    type: ApplicationType
    author_user_id: UUID = Field(description="Автор заявки (identity_db.users.id)")
    club_id: UUID | None = Field(
        default=None, description="Секция-организатор, если заявка на мероприятие подана от имени секции"
    )
    event: EventApplicationData | None = None
    club_page: ClubPageApplicationData | None = None
    result_object_id: UUID = Field(
        description="Id мероприятия или секции, назначенный Moderation при одобрении"
    )
    processed_by: UUID = Field(description="Модератор (identity_db.users.id)")
    processed_at: UtcDatetime

    @model_validator(mode="after")
    def _data_matches_type(self) -> Self:
        if self.type == "event" and (self.event is None or self.club_page is not None):
            raise ValueError("Для type = event нужен блок event и не нужен club_page")
        if self.type == "club_page" and (self.club_page is None or self.event is not None):
            raise ValueError("Для type = club_page нужен блок club_page и не нужен event")
        return self


class ApplicationRejected(BaseEvent):
    """Модератор отклонил заявку. Notifications сообщает автору комментарий модератора."""

    event_type: ClassVar[str] = "ApplicationRejected"
    producer: ClassVar[Service] = Service.MODERATION
    routing_key: ClassVar[str] = "moderation.application.rejected"
    consumers: ClassVar[tuple[Service, ...]] = (Service.NOTIFICATIONS,)
    stage: ClassVar[Stage] = "stable"

    application_id: UUID = Field(description="moderation_db.applications.id")
    type: ApplicationType
    author_user_id: UUID = Field(description="Автор заявки (identity_db.users.id)")
    club_id: UUID | None = Field(default=None, description="Секция-организатор заявки")
    moderator_comment: str = Field(min_length=1, max_length=1000, description="Причина отказа, обязательна")
    processed_by: UUID = Field(description="Модератор (identity_db.users.id)")
    processed_at: UtcDatetime


class ComplaintResolved(BaseEvent):
    """Черновик. Окончательное решение по жалобе: подтвердилась или не подтвердилась.

    Публикуется при решениях `confirm` и `reject`; при `extra_check` жалоба не закрыта
    и событие не публикуется. Notifications сообщает автору жалобы результат.
    """

    event_type: ClassVar[str] = "ComplaintResolved"
    producer: ClassVar[Service] = Service.MODERATION
    routing_key: ClassVar[str] = "moderation.complaint.resolved"
    consumers: ClassVar[tuple[Service, ...]] = (Service.NOTIFICATIONS,)

    complaint_id: UUID = Field(description="moderation_db.complaints.id")
    target_type: Literal["event", "club"]
    target_id: UUID = Field(description="Мероприятие (events.id) или секция (clubs.id)")
    target_version_id: UUID = Field(description="Версия текста на момент подачи жалобы")
    author_user_id: UUID = Field(description="Автор жалобы (identity_db.users.id)")
    decision: Literal["confirmed", "rejected"] = Field(
        description="confirmed - жалоба подтвердилась (status = true), rejected - нет (status = false)"
    )
    moderator_comment: str | None = Field(default=None, max_length=1000)
    processed_by: UUID = Field(description="Модератор (identity_db.users.id)")
    processed_at: UtcDatetime
