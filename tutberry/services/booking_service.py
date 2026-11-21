"""Booking use case with explicit dependency ports."""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Protocol
from uuid import UUID

from tutberry.domain.booking import Booking, BookingError, BookingPrice, RentalPeriod


class BookingRepository(Protocol):
    def add(self, booking: Booking) -> None: ...
    def find_overlapping(self, listing_id: UUID, period: RentalPeriod) -> list[Booking]: ...


class IdGenerator(Protocol):
    def new_id(self) -> UUID: ...


class BookingNotifier(Protocol):
    def booking_created(self, booking: Booking) -> None: ...


@dataclass(frozen=True)
class BookingRequest:
    listing_id: UUID
    tenant_id: UUID
    start_date: date
    end_date: date
    daily_rate: Decimal
    deposit: Decimal


class BookingService:
    def __init__(self, repository: BookingRepository, ids: IdGenerator, notifier: BookingNotifier):
        self.repository = repository
        self.ids = ids
        self.notifier = notifier

    def create(self, request: BookingRequest) -> Booking:
        period = RentalPeriod(request.start_date, request.end_date)
        if request.daily_rate <= 0:
            raise BookingError("Daily rate must be positive")
        if self.repository.find_overlapping(request.listing_id, period):
            raise BookingError("Requested dates are unavailable")
        price = BookingPrice(request.daily_rate * period.days, request.deposit)
        booking = Booking(self.ids.new_id(), request.listing_id, request.tenant_id, period, price)
        self.repository.add(booking)
        self.notifier.booking_created(booking)
        return booking
