"""Integration checks for serialized owner calendar updates."""
from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest
from django.db import transaction

from tutberry.adapters.sql_booking import SqlBookingRepository
from tutberry.domain.booking import Booking, BookingPrice, RentalPeriod
from tutberry.models import ListingAvailabilityRecord, ListingRecord
from tutberry.services.availability_service import (
    AvailabilityConflict,
    set_listing_block,
)


@pytest.mark.django_db(transaction=True)
def test_owner_block_cannot_overlap_existing_booking():
    owner_id = uuid4()
    listing = ListingRecord.objects.create(
        owner_id=owner_id, title="Drill", daily_rate=Decimal(100),
        deposit=Decimal(200), status="active",
    )
    booking = Booking(
        uuid4(), listing.id, uuid4(),
        RentalPeriod(date(2030, 7, 10), date(2030, 7, 12)),
        BookingPrice(Decimal(300), Decimal(200)),
    )
    with transaction.atomic():
        SqlBookingRepository().add(booking)
    with pytest.raises(AvailabilityConflict):
        set_listing_block(
            listing_id=listing.id, owner_id=owner_id,
            start_date=date(2030, 7, 12), end_date=date(2030, 7, 14),
        )
    assert not ListingAvailabilityRecord.objects.exists()
    block = set_listing_block(
        listing_id=listing.id, owner_id=owner_id,
        start_date=date(2030, 7, 13), end_date=date(2030, 7, 14),
    )
    assert block.is_blocked


@pytest.mark.django_db
def test_other_owner_cannot_create_block():
    listing = ListingRecord.objects.create(
        owner_id=uuid4(), title="Saw", daily_rate=100, deposit=200, status="active",
    )
    with pytest.raises(ListingRecord.DoesNotExist):
        set_listing_block(
            listing_id=listing.id, owner_id=uuid4(),
            start_date=date(2030, 7, 10), end_date=date(2030, 7, 11),
        )
