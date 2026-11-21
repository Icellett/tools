"""Test adapter; not safe for concurrent production bookings."""
from uuid import UUID

from tutberry.domain.booking import Booking, BookingStatus, RentalPeriod


class InMemoryBookingRepository:
    def __init__(self) -> None:
        self.bookings: list[Booking] = []

    def add(self, booking: Booking) -> None:
        self.bookings.append(booking)

    def find_overlapping(self, listing_id: UUID, period: RentalPeriod) -> list[Booking]:
        return [
            booking for booking in self.bookings
            if booking.listing_id == listing_id
            and booking.status != BookingStatus.CANCELLED
            and booking.period.overlaps(period)
        ]
