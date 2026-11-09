# tusumba-contracts

Общий пакет со схемами событий брокера сообщений (Pydantic-модели) для всех сервисов.

**Ответственный:** Артем Вдовин (задача #18889).

## Таблица событий

| Событие | Routing key | Публикует | Потребляет | Когда | Статус |
|---|---|---|---|---|---|
| `ApplicationApproved` | `moderation.application.approved` | moderation-service | events-service, notifications-service | Модератор одобрил заявку на мероприятие или страницу секции | stable |
| `ApplicationRejected` | `moderation.application.rejected` | moderation-service | notifications-service | Модератор отклонил заявку, комментарий обязателен | stable |
| `ComplaintResolved` | `moderation.complaint.resolved` | moderation-service | notifications-service | Жалоба подтвердилась или не подтвердилась (не при дополнительной проверке) | draft |
| `EventPublished` | `events.event.published` | events-service | notifications-service | Мероприятие создано по одобренной заявке и опубликовано | draft |
| `EventUpdated` | `events.event.updated` | events-service | notifications-service | Мероприятие отредактировано | draft |
| `TeamInvitationSent` | `events.team_invitation.sent` | events-service | notifications-service | Пользователь приглашён в команду мероприятия по нику или email | draft |
| `TicketPurchased` | `ticketing.ticket.purchased` | ticketing-service | notifications-service | Платёж прошёл, билеты проданы | draft |
| `RegistrationChanged` | `ticketing.registration.changed` | ticketing-service | notifications-service | Запись на мероприятие создана, изменена или снята | draft |
| `FriendRequested` | `identity.friend_request.created` | identity-service | notifications-service | Отправлен запрос в друзья | draft |
| `EventInvitationSent` | `identity.event_invitation.sent` | identity-service | notifications-service | Друг приглашён на мероприятие | draft |

`stable` - схема согласована (Спринт 1), `draft` - черновик, поля ещё могут измениться.
Поля событий описаны в классах пакета (`tusumba_contracts.events`). Данные заявки в `ApplicationApproved`
(`event` или `club_page` по полю `type`) совпадают со схемами `EventApplicationData` и `ClubPageApplicationData`
в OpenAPI Moderation (#18890). Черновики Events & Clubs сверены с её OpenAPI (#18891): `EventPublished` -
как `EventInternal`, `TeamInvitationSent` - как `TeamInvitation`, `changed_fields` в `EventUpdated` - поля `EventUpdate`.

Состав и поля событий согласуются с командами сервисов, поэтому любое изменение схемы идёт через PR с одобрением
ответственного и затронутых команд.

## Обёртка сообщения

Каждое сообщение в брокере - объект `EventEnvelope` в JSON:

| Поле | Тип | Что это |
|---|---|---|
| `event_id` | UUID | Уникальный id сообщения; по нему получатель отбрасывает повторы |
| `event_type` | строка | Имя события, например `ApplicationApproved` |
| `occurred_at` | время ISO 8601, UTC | Когда произошло событие |
| `version` | целое, от 1 | Версия схемы `payload` |
| `producer` | `identity`, `events`, `ticketing`, `moderation`, `notifications` | Сервис-отправитель |
| `payload` | объект | Данные события, схема задаётся парой `event_type` + `version` |

```json
{
  "event_id": "5b1f6c2e-8d4a-4f3b-9e7c-1a2b3c4d5e6f",
  "event_type": "ApplicationApproved",
  "occurred_at": "2026-11-10T08:00:00Z",
  "version": 1,
  "producer": "moderation",
  "payload": {
    "application_id": "11111111-1111-4111-8111-111111111111",
    "type": "event",
    "author_user_id": "22222222-2222-4222-8222-222222222222",
    "club_id": null,
    "result_object_id": "33333333-3333-4333-8333-333333333333",
    "event": {
      "title": "Посвят ФИТ",
      "description": "Концерт, конкурсы и дискотека",
      "date": "2026-12-05",
      "place_address": "Новосибирск, ул. Пирогова, 2",
      "is_free": false,
      "price": {"amount": 30000, "currency": "RUB"}
    },
    "processed_by": "44444444-4444-4444-8444-444444444444",
    "processed_at": "2026-11-10T08:00:00Z"
  }
}
```

## Правила

**Exchange и очереди.**

- Один exchange `tusumba.events`, тип `topic`, durable. Все события публикуются в него.
- Routing key: `<producer>.<сущность>.<действие>`, строчными, сущность в `snake_case`: `moderation.application.approved`.
- Очереди объявляют получатели: `<сервис>.<назначение>`, например `notifications.applications`, durable,
  с привязкой к нужным routing key.

**Имена событий.** `event_type` - PascalCase в прошедшем времени: `ApplicationApproved`, `TicketPurchased`.

**Изменение схемы.**

- Совместимо, без новой версии: добавить **необязательное** поле со значением по умолчанию.
- Несовместимо, нужна новая версия: удалить или переименовать поле, сделать поле обязательным, сменить тип или смысл
  поля, добавить значение в перечисление.
- Новая версия - новый класс с тем же `event_type` и `version = N + 1`. Отправитель публикует обе версии, пока все
  получатели не перейдут на новую.
- Получатели игнорируют неизвестные поля - так настроены модели пакета (`extra="ignore"`).

**Доставка и повторы.**

- Отправитель публикует через transactional outbox. Конверт (`event.envelope()`) создаётся один раз при записи
  в outbox, поэтому повторная публикация отправляет тот же `event_id`.
- Брокер может доставить сообщение повторно. Получатель хранит обработанные `event_id` и пропускает повторы.

**Данные.** Время только UTC, деньги - `{"amount": <копейки>, "currency": "RUB"}`, идентификаторы - UUID.

## Стек

Python 3.12, Pydantic v2.

## Подключение

В `requirements.txt` / `pyproject.toml` сервиса, по тегу версии:

```text
tusumba-contracts @ git+https://github.com/tusumba/tusumba-contracts.git@v0.1.0
```

## Разработка

```bash
pip install -e ".[dev]"
pytest
ruff check . && ruff format --check .
mypy
```

Новое событие: класс в `tusumba_contracts/events/`, экспорт в `events/__init__.py` и `tusumba_contracts/__init__.py`,
запись в `ALL_EVENTS` (`registry.py`), пример в `tests/conftest.py`, строка в таблице событий.
Релиз: тег `vX.Y.Z` на main, версию поднять в `pyproject.toml`.

## Документация

Wiki проекта: https://ai.nsu.ru/projects/tusumba/wiki/Архитектура. Задачи ведутся в Redmine: https://ai.nsu.ru/projects/tusumba. Issues и Wiki GitHub выключены.
