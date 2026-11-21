from datetime import date
from decimal import Decimal
from uuid import UUID

import pytest

from tutberry.adapters.in_memory import InMemoryBookingRepository
from tutberry.domain.booking import BookingError
from tutberry.services.booking_service import BookingRequest, BookingService


class FixedIds:
    def new_id(self):
        return UUID(int=3)


class SpyNotifier:
    def __init__(self):
        self.sent = []

    def booking_created(self, booking):
        self.sent.append(booking.id)


def test_booking_created_with_fixed_price_and_notification():
    repository = InMemoryBookingRepository()
    notifier = SpyNotifier()
    service = BookingService(repository, FixedIds(), notifier)
    request = BookingRequest(UUID(int=1), UUID(int=2), date(2030, 1, 1), date(2030, 1, 3), Decimal('500'), Decimal('2000'))
    booking = service.create(request)
    assert booking.price.rent == Decimal('1500')
    assert booking.price.total == Decimal('3500')
    assert len(repository.bookings) == 1
    assert notifier.sent == [booking.id]
    with pytest.raises(BookingError, match='unavailable'):
        service.create(request)
