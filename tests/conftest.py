import datetime as dt
from uuid import UUID

import pytest

from tusumba_contracts import (
    ApplicationApproved,
    ApplicationRejected,
    BaseEvent,
    ComplaintResolved,
    EventApplicationData,
    EventInvitationSent,
    EventPublished,
    EventUpdated,
    FriendRequested,
    Money,
    RegistrationChanged,
    TeamInvitationSent,
    TicketPurchased,
)

U1 = UUID("11111111-1111-4111-8111-111111111111")
U2 = UUID("22222222-2222-4222-8222-222222222222")
U3 = UUID("33333333-3333-4333-8333-333333333333")
U4 = UUID("44444444-4444-4444-8444-444444444444")
NOW = dt.datetime(2026, 11, 10, 8, 0, tzinfo=dt.UTC)
DAY = dt.date(2026, 12, 5)


def sample_events() -> list[BaseEvent]:
    """По одному корректному экземпляру каждого события."""
    return [
        ApplicationApproved(
            application_id=U1,
            author_user_id=U2,
            type="event",
            result_object_id=U3,
            event=EventApplicationData(
                title="Посвят ФИТ",
                description="Концерт и конкурсы",
                date=DAY,
                place_address="Новосибирск, ул. Пирогова, 2",
                is_free=False,
                price=Money(amount=30000),
            ),
            processed_by=U4,
            processed_at=NOW,
        ),
        ApplicationRejected(
            application_id=U1,
            type="club_page",
            author_user_id=U2,
            moderator_comment="Не указано расписание встреч",
            processed_by=U4,
            processed_at=NOW,
        ),
        ComplaintResolved(
            complaint_id=U1,
            target_type="event",
            target_id=U2,
            target_version_id=U3,
            author_user_id=U4,
            decision="confirmed",
            processed_by=U4,
            processed_at=NOW,
        ),
        EventPublished(
            event_id=U1,
            current_version_id=U2,
            title="Посвят ФИТ",
            date=DAY,
            place_address="НГУ",
            is_free=True,
            status="not_confirmed",
            created_by_user_id=U3,
        ),
        EventUpdated(
            event_id=U1,
            current_version_id=U2,
            title="Посвят ФИТ",
            date=DAY,
            place_address="НГУ",
            is_free=True,
            status="confirmed",
            edited_by=U3,
            changed_fields=["date"],
        ),
        TeamInvitationSent(
            invitation_id=U1,
            event_id=U2,
            event_title="Посвят ФИТ",
            invitee_email="ivan@example.com",
            role="editor",
            invited_by=U3,
        ),
        TicketPurchased(
            purchase_id=U1,
            event_id=U2,
            user_id=U3,
            ticket_ids=[U4],
            quantity=1,
            total=Money(amount=30000),
            purchased_at=NOW,
        ),
        RegistrationChanged(
            registration_id=U1,
            event_id=U2,
            user_id=U3,
            action="created",
            status="going",
            visibility="public",
            source="free_signup",
        ),
        FriendRequested(friend_request_id=U1, from_user_id=U2, to_user_id=U3),
        EventInvitationSent(invitation_id=U1, event_id=U2, from_user_id=U3, to_user_id=U4),
    ]


@pytest.fixture(params=sample_events(), ids=lambda e: e.event_type)
def any_event(request: pytest.FixtureRequest) -> BaseEvent:
    event: BaseEvent = request.param
    return event
