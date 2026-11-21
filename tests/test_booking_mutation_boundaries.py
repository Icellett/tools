"""Boundary and state-transition tests for booking-domain mutation analysis."""
from datetime import date
from decimal import Decimal
from uuid import UUID

import pytest

from tutberry.domain.booking import (
    Booking,
    BookingError,
    BookingPrice,
    BookingStatus,
    RentalPeriod,
)


def booking(status=BookingStatus.PENDING):
    return Booking(
        UUID(int=11), UUID(int=12), UUID(int=13),
        RentalPeriod(date(2030, 1, 10), date(2030, 1, 12)),
        BookingPrice(Decimal(200), Decimal(50)),
        status=status,
    )


def test_period_same_day_inclusive_and_exact_length():
    assert RentalPeriod(date(2030, 1, 10), date(2030, 1, 10)).days == 1
    assert RentalPeriod(date(2030, 1, 10), date(2030, 1, 12)).days == 3


@pytest.mark.parametrize(
    ("left", "right", "expected"),
    [
        ((10, 12), (12, 15), True),
        ((10, 12), (8, 10), True),
        ((10, 12), (13, 15), False),
        ((10, 12), (7, 9), False),
        ((10, 12), (11, 11), True),
        ((10, 12), (8, 15), True),
    ],
)
def test_overlap_boundary_both_directions(left, right, expected):
    a = RentalPeriod(date(2030, 1, left[0]), date(2030, 1, left[1]))
    b = RentalPeriod(date(2030, 1, right[0]), date(2030, 1, right[1]))
    assert a.overlaps(b) is expected
    assert b.overlaps(a) is expected


def test_price_exact_sum_and_zero_boundaries():
    assert BookingPrice(Decimal("12.50"), Decimal("3.25")).total == Decimal("15.75")
    assert BookingPrice(Decimal(0), Decimal(0)).total == Decimal(0)
    assert BookingPrice(Decimal(0), Decimal(10)).total == Decimal(10)


@pytest.mark.parametrize("rent,deposit", [("-0.01", "0"), ("0", "-0.01")])
def test_negative_amounts_rejected_independently(rent, deposit):
    with pytest.raises(BookingError):
        BookingPrice(Decimal(rent), Decimal(deposit))


@pytest.mark.parametrize(
    ("action", "allowed", "result"),
    [
        ("approve", BookingStatus.PENDING, BookingStatus.APPROVED),
        ("mark_paid", BookingStatus.APPROVED, BookingStatus.PAID),
        ("hand_over", BookingStatus.PAID, BookingStatus.ACTIVE),
        ("complete", BookingStatus.ACTIVE, BookingStatus.COMPLETED),
    ],
)
def test_transition_allowed_only_from_exact_status(action, allowed, result):
    for status in BookingStatus:
        current = booking(status)
        if status == allowed:
            updated = getattr(current, action)()
            assert updated.status == result
            assert current.status == status
            assert updated.id == current.id
            assert updated.listing_id == current.listing_id
            assert updated.tenant_id == current.tenant_id
            assert updated.period == current.period
            assert updated.price == current.price
        else:
            with pytest.raises(BookingError):
                getattr(current, action)()


@pytest.mark.parametrize("status", list(BookingStatus))
def test_cancellation_status_matrix(status):
    current = booking(status)
    if status in (BookingStatus.PENDING, BookingStatus.APPROVED):
        cancelled = current.cancel("  changed plans  ")
        assert cancelled.status == BookingStatus.CANCELLED
        assert cancelled.cancellation_reason == "changed plans"
        assert current.status == status
    else:
        with pytest.raises(BookingError):
            current.cancel("changed plans")


@pytest.mark.parametrize("reason", ["", " ", "\t\n"])
def test_cancellation_rejects_blank_reason(reason):
    with pytest.raises(BookingError):
        booking().cancel(reason)


def test_booking_status_wire_values_are_stable():
    # These strings are persisted and returned through the API.
    assert {status.name: status.value for status in BookingStatus} == {
        "PENDING": "pending",
        "APPROVED": "approved",
        "PAID": "paid",
        "ACTIVE": "active",
        "COMPLETED": "completed",
        "CANCELLED": "cancelled",
        "DISPUTED": "disputed",
    }


@pytest.mark.parametrize(
    ("operation", "status", "expected_message"),
    [
        ("approve", BookingStatus.APPROVED, "Only pending bookings can be approved"),
        ("mark_paid", BookingStatus.PENDING, "Payment requires an approved booking"),
        ("hand_over", BookingStatus.PENDING, "Handover requires confirmed payment"),
        ("complete", BookingStatus.PENDING, "Only active bookings can be completed"),
    ],
)
def test_invalid_transition_reports_specific_reason(operation, status, expected_message):
    with pytest.raises(BookingError, match=f"^{expected_message}$"):
        getattr(booking(status), operation)()


def test_period_and_price_validation_messages():
    with pytest.raises(BookingError, match="Rental period end cannot precede start"):
        RentalPeriod(date(2030, 1, 11), date(2030, 1, 10))
    with pytest.raises(BookingError, match="Amounts cannot be negative"):
        BookingPrice(Decimal(-1), Decimal(0))
    with pytest.raises(BookingError, match="Cancellation reason is required"):
        booking().cancel("   ")
    with pytest.raises(
        BookingError, match="Booking cannot be cancelled in its current status"
    ):
        booking(BookingStatus.PAID).cancel("reason")
