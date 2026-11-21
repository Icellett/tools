"""Real PostgreSQL integration checks for handwritten SQL and exclusion rule."""
from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest
from django.db import IntegrityError, connection, transaction

from tutberry.adapters.sql_booking import SqlBookingRepository
from tutberry.domain.booking import Booking, BookingError, BookingPrice, RentalPeriod
from tutberry.models import ListingRecord


@pytest.mark.django_db(transaction=True)
def test_sql_repository_round_trip_and_overlap():
    listing = ListingRecord.objects.create(
        owner_id=uuid4(), title="Drill", daily_rate=Decimal("500"),
        deposit=Decimal("1000"), status="active",
    )
    repo = SqlBookingRepository()
    booking = Booking(
        uuid4(), listing.id, uuid4(),
        RentalPeriod(date(2030, 1, 1), date(2030, 1, 3)),
        BookingPrice(Decimal("1500"), Decimal("1000")),
    )
    with transaction.atomic():
        repo.add(booking)
    found = repo.find_overlapping(listing.id, RentalPeriod(date(2030, 1, 3), date(2030, 1, 4)))
    assert len(found) == 1
    assert found[0] == booking
    assert repo.find_overlapping(listing.id, RentalPeriod(date(2030, 1, 4), date(2030, 1, 5))) == []


@pytest.mark.django_db(transaction=True)
def test_database_rejects_overlapping_booking_even_without_service():
    listing = ListingRecord.objects.create(
        owner_id=uuid4(), title="Saw", daily_rate=Decimal("200"),
        deposit=Decimal("500"), status="active",
    )
    repo = SqlBookingRepository()
    def booking(start, end):
        return Booking(
            uuid4(), listing.id, uuid4(), RentalPeriod(start, end),
            BookingPrice(Decimal("200"), Decimal("500")),
        )
    with transaction.atomic():
        repo.add(booking(date(2030, 2, 1), date(2030, 2, 3)))
    with pytest.raises(BookingError, match="unavailable"):
        with transaction.atomic():
            repo.add(booking(date(2030, 2, 3), date(2030, 2, 5)))
    with transaction.atomic():
        repo.add(booking(date(2030, 2, 4), date(2030, 2, 5)))
