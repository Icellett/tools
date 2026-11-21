"""Django persistence adapter; called under a listing-row transaction lock."""
from uuid import UUID

from tutberry.domain.booking import Booking, BookingPrice, BookingStatus, RentalPeriod
from tutberry.models import BookingRecord


class DjangoBookingRepository:
    def add(self, booking: Booking) -> None:
        BookingRecord.objects.create(
            id=booking.id,
            listing_id=booking.listing_id,
            tenant_id=booking.tenant_id,
            start_date=booking.period.start_date,
            end_date=booking.period.end_date,
            rent=booking.price.rent,
            deposit=booking.price.deposit,
            status=booking.status.value,
            cancellation_reason=booking.cancellation_reason,
        )

    def find_overlapping(self, listing_id: UUID, period: RentalPeriod) -> list[Booking]:
        records = BookingRecord.objects.filter(
            listing_id=listing_id,
            start_date__lte=period.end_date,
            end_date__gte=period.start_date,
        ).exclude(status=BookingStatus.CANCELLED.value)
        return [
            Booking(
                id=record.id,
                listing_id=record.listing_id,
                tenant_id=record.tenant_id,
                period=RentalPeriod(record.start_date, record.end_date),
                price=BookingPrice(record.rent, record.deposit),
                status=BookingStatus(record.status),
                cancellation_reason=record.cancellation_reason,
            )
            for record in records
        ]
