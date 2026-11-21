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
from tutberry.domain.listing import Listing, ListingError, ListingStatus
from tutberry.domain.payment import Payment, PaymentError, PaymentStatus

A = UUID(int=1)
B = UUID(int=2)


def test_inclusive_period_and_overlap():
    first = RentalPeriod(date(2030, 1, 1), date(2030, 1, 2))
    assert first.days == 2
    assert first.overlaps(RentalPeriod(date(2030, 1, 2), date(2030, 1, 3)))


def test_invalid_period_rejected():
    with pytest.raises(BookingError):
        RentalPeriod(date(2030, 2, 2), date(2030, 2, 1))


def test_booking_lifecycle_and_cancelled_guard():
    booking = Booking(A, B, A, RentalPeriod(date(2030, 1, 1), date(2030, 1, 2)), BookingPrice(Decimal(200), Decimal(100)))
    assert booking.price.total == Decimal(300)
    assert booking.approve().mark_paid().hand_over().complete().status == BookingStatus.COMPLETED
    cancelled = booking.cancel('Changed plans')
    assert cancelled.cancellation_reason == 'Changed plans'
    with pytest.raises(BookingError):
        cancelled.approve()


def test_listing_moderation():
    listing = Listing(A, B, 'Drill', Decimal(100), Decimal(300))
    assert listing.submit().approve().status == ListingStatus.ACTIVE
    with pytest.raises(ListingError):
        Listing(A, B, '', Decimal(100), Decimal(300)).submit()


def test_payment_requires_provider_confirmation():
    payment = Payment(A, B, Decimal(100))
    assert payment.confirm('provider-1').status == PaymentStatus.SUCCESS
    with pytest.raises(PaymentError):
        payment.confirm('')
