# tusumba-contracts

Общий пакет со схемами событий брокера сообщений (Pydantic-модели) для всех сервисов.

**Ответственный:** Артем Вдовин (задача #18889).

## Что внутри

Схемы событий, которыми сервисы обмениваются через RabbitMQ:

| Событие | Публикует | Потребляет |
|---|---|---|
| `FriendRequested`, `EventInvitationSent` | identity-service | notifications-service |
| `EventPublished`, `EventUpdated` | events-service | notifications-service |
| `TicketPurchased`, `RegistrationChanged` | ticketing-service | notifications-service |
| `ApplicationApproved` | moderation-service | events-service, notifications-service |
| `ComplaintResolved` | moderation-service | notifications-service |

Состав и поля событий согласуются с командами сервисов, поэтому любое изменение схемы идёт через PR с одобрением ответственного и затронутых команд.

## Стек

Python 3.12, Pydantic v2.

## Документация

Wiki проекта: https://ai.nsu.ru/projects/tusumba/wiki/Архитектура. Задачи ведутся в Redmine: https://ai.nsu.ru/projects/tusumba. Issues и Wiki GitHub выключены.

## Правила работы

Ветки, коммиты, pull request и code review описаны в [CONTRIBUTING.md](https://github.com/tusumba/.github/blob/main/CONTRIBUTING.md). Коротко:

- ветка называется `feature/<номер задачи Redmine>-<пара слов>`, например `feature/18901-login`;
- номер задачи указывается в каждом коммите и в названии PR;
- в `main` изменения попадают только через PR с одним одобрением и зелёным CI, прямой push и force push запрещены.
