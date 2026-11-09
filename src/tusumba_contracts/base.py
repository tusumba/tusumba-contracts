"""Базовый класс события и обёртка сообщения."""

from datetime import UTC, datetime
from typing import Any, ClassVar, Literal, Self, cast
from uuid import UUID, uuid4

from pydantic import Field, model_validator

from .types import ContractModel, Service, UtcDatetime

Stage = Literal["stable", "draft"]


class BaseEvent(ContractModel):
    """Данные события (`payload` обёртки).

    Каждое событие задаёт метаданные в атрибутах класса; в JSON они не попадают.
    """

    event_type: ClassVar[str]
    """Имя события, PascalCase в прошедшем времени, например `ApplicationApproved`."""
    version: ClassVar[int] = 1
    """Версия схемы. Несовместимое изменение - новый класс с тем же `event_type` и `version + 1`."""
    producer: ClassVar[Service]
    """Сервис-отправитель."""
    routing_key: ClassVar[str]
    """Routing key в exchange `tusumba.events`: `<producer>.<сущность>.<действие>`."""
    consumers: ClassVar[tuple[Service, ...]] = ()
    """Сервисы-получатели (для документации; брокер это не проверяет)."""
    stage: ClassVar[Stage] = "draft"
    """`stable` - схема согласована, `draft` - черновик, поля могут измениться."""

    def envelope(
        self,
        *,
        event_id: UUID | None = None,
        occurred_at: datetime | None = None,
    ) -> "EventEnvelope[Self]":
        """Обернуть событие. Вызывать один раз - при записи в outbox, и хранить результат.

        Повторная публикация из outbox должна отправлять тот же `event_id`, иначе получатель
        не распознает повтор.
        """
        envelope_cls = cast(Any, EventEnvelope)[type(self)]
        return envelope_cls(  # type: ignore[no-any-return]
            event_id=event_id or uuid4(),
            event_type=self.event_type,
            occurred_at=occurred_at or datetime.now(UTC),
            version=self.version,
            producer=self.producer,
            payload=self,
        )


class EventEnvelope[P: BaseEvent](ContractModel):
    """Общая обёртка всех сообщений брокера."""

    event_id: UUID = Field(description="Уникальный id сообщения; по нему получатель отбрасывает повторы")
    event_type: str = Field(description="Имя события, совпадает с `event_type` класса payload")
    occurred_at: UtcDatetime = Field(description="Когда произошло событие, UTC")
    version: int = Field(ge=1, description="Версия схемы payload")
    producer: Service = Field(description="Сервис-отправитель")
    payload: P

    @model_validator(mode="after")
    def _payload_matches_header(self) -> Self:
        payload: Any = self.payload
        expected = (payload.event_type, payload.version, payload.producer)
        actual = (self.event_type, self.version, self.producer)
        if expected != actual:
            raise ValueError(
                f"Заголовок {actual} не соответствует классу payload {type(payload).__name__} {expected}"
            )
        return self
