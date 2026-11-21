"""PostgreSQL booking repository using parameterized handwritten SQL.

Implements the synchronous BookingRepository port from LR 3 without ORM.
The caller owns the transaction and listing-row lock.
"""
from uuid import UUID

from django.db import IntegrityError, connection

from tutberry.domain.booking import (
    Booking,
    BookingError,
    BookingPrice,
    BookingStatus,
    RentalPeriod,
)

_INSERT = """
INSERT INTO tutberry_bookingrecord
    (id, listing_id, tenant_id, start_date, end_date, rent, deposit, status, cancellation_reason)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

_FIND_OVERLAPPING = """
SELECT id, listing_id, tenant_id, start_date, end_date,
       rent, deposit, status, cancellation_reason
FROM tutberry_bookingrecord
WHERE listing_id = %s
  AND status <> 'cancelled'
  AND daterange(start_date, end_date + 1, '[)')
      && daterange(%s::date, %s::date + 1, '[)')
"""


def _booking(row):
    return Booking(
        id=UUID(str(row[0])),
        listing_id=UUID(str(row[1])),
        tenant_id=UUID(str(row[2])),
        period=RentalPeriod(row[3], row[4]),
        price=BookingPrice(row[5], row[6]),
        status=BookingStatus(row[7]),
        cancellation_reason=row[8],
    )


class SqlBookingRepository:
    def add(self, booking: Booking) -> None:
        try:
            with connection.cursor() as cursor:
                cursor.execute(_INSERT, [
                    str(booking.id), str(booking.listing_id), str(booking.tenant_id),
                    booking.period.start_date, booking.period.end_date,
                    booking.price.rent, booking.price.deposit,
                    booking.status.value, booking.cancellation_reason,
                ])
        except IntegrityError as exc:
            # PostgreSQL SQLSTATE 23P01: exclusion constraint violation.
            if getattr(getattr(exc, "__cause__", None), "sqlstate", None) == "23P01":
                raise BookingError("Requested dates are unavailable") from exc
            raise

    def find_overlapping(self, listing_id: UUID, period: RentalPeriod) -> list[Booking]:
        with connection.cursor() as cursor:
            cursor.execute(_FIND_OVERLAPPING, [
                str(listing_id), period.start_date, period.end_date,
            ])
            return [_booking(row) for row in cursor.fetchall()]
