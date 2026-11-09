"""Согласованные события Спринта 1. Черновики проверяются только разбором в test_envelope."""

from typing import Any

import pytest
from pydantic import ValidationError

from conftest import DAY, NOW, U1, U2, U3, U4
from tusumba_contracts import (
    ApplicationApproved,
    ApplicationRejected,
    ClubPageApplicationData,
    EventApplicationData,
)

EVENT = {
    "title": "Посвят ФИТ",
    "description": "Концерт",
    "date": "2026-12-05",
    "place_address": "НГУ",
    "is_free": True,
}
CLUB_PAGE = {"name": "Настольные игры", "description": "Играем по пятницам"}


def approved(**blocks: Any) -> ApplicationApproved:
    return ApplicationApproved.model_validate(
        {
            "application_id": str(U1),
            "author_user_id": str(U2),
            "result_object_id": str(U3),
            "processed_by": str(U4),
            "processed_at": "2026-11-10T08:00:00Z",
        }
        | blocks
    )


@pytest.mark.parametrize(
    ("blocks", "attr", "expected"),
    [
        ({"type": "event", "event": EVENT}, "event", EventApplicationData),
        ({"type": "club_page", "club_page": CLUB_PAGE}, "club_page", ClubPageApplicationData),
    ],
)
def test_approved_data_by_type(blocks: dict[str, Any], attr: str, expected: type) -> None:
    assert isinstance(getattr(approved(**blocks), attr), expected)


@pytest.mark.parametrize(
    "blocks",
    [
        {"type": "event"},
        {"type": "event", "club_page": CLUB_PAGE},
        {"type": "club_page", "event": EVENT, "club_page": CLUB_PAGE},
    ],
)
def test_approved_block_must_match_type(blocks: dict[str, Any]) -> None:
    with pytest.raises(ValidationError, match="нужен блок"):
        approved(**blocks)


def test_paid_event_requires_price() -> None:
    with pytest.raises(ValidationError, match="цена"):
        EventApplicationData(title="T", description="D", date=DAY, place_address="НГУ", is_free=False)


def test_rejected_requires_comment() -> None:
    with pytest.raises(ValidationError):
        ApplicationRejected(
            application_id=U1,
            type="event",
            author_user_id=U2,
            moderator_comment="",
            processed_by=U4,
            processed_at=NOW,
        )
