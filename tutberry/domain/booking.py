"""Booking aggregate and value objects (no Django imports)."""
from dataclasses import dataclass, replace
from datetime import date
from decimal import Decimal
from enum import Enum
from uuid import UUID


class BookingError(ValueError):
    """Invalid booking domain operation."""


class BookingStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    PAID = "paid"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"


@dataclass(frozen=True)
class RentalPeriod:
    start_date: date
    end_date: date

    def __post_init__(self) -> None:
        if self.end_date < self.start_date:
            raise BookingError("Rental period end cannot precede start")

    @property
    def days(self) -> int:
        return (self.end_date - self.start_date).days + 1

    def overlaps(self, other: "RentalPeriod") -> bool:
        return self.start_date <= other.end_date and other.start_date <= self.end_date


@dataclass(frozen=True)
class BookingPrice:
    rent: Decimal
    deposit: Decimal

    def __post_init__(self) -> None:
        if self.rent < 0 or self.deposit < 0:
            raise BookingError("Amounts cannot be negative")

    @property
    def total(self) -> Decimal:
        return self.rent + self.deposit


@dataclass(frozen=True)
class Booking:
    id: UUID
    listing_id: UUID
    tenant_id: UUID
    period: RentalPeriod
    price: BookingPrice
    status: BookingStatus = BookingStatus.PENDING
    cancellation_reason: str | None = None

    def approve(self) -> "Booking":
        if self.status != BookingStatus.PENDING:
            raise BookingError("Only pending bookings can be approved")
        return replace(self, status=BookingStatus.APPROVED)

    def cancel(self, reason: str) -> "Booking":
        if not reason.strip():
            raise BookingError("Cancellation reason is required")
        if self.status not in {BookingStatus.PENDING, BookingStatus.APPROVED}:
            raise BookingError("Booking cannot be cancelled in its current status")
        return replace(self, status=BookingStatus.CANCELLED, cancellation_reason=reason.strip())

    def mark_paid(self) -> "Booking":
        if self.status != BookingStatus.APPROVED:
            raise BookingError("Payment requires an approved booking")
        return replace(self, status=BookingStatus.PAID)

    def hand_over(self) -> "Booking":
        if self.status != BookingStatus.PAID:
            raise BookingError("Handover requires confirmed payment")
        return replace(self, status=BookingStatus.ACTIVE)

    def complete(self) -> "Booking":
        if self.status != BookingStatus.ACTIVE:
            raise BookingError("Only active bookings can be completed")
        return replace(self, status=BookingStatus.COMPLETED)
