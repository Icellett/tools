"""PostgreSQL integration tests for the availability expand migration."""
from datetime import date
from uuid import uuid4

import pytest
from django.db import IntegrityError, transaction

from tutberry.models import ListingAvailabilityRecord, ListingRecord


@pytest.mark.django_db
def test_listing_availability_block_round_trip():
    listing = ListingRecord.objects.create(
        owner_id=uuid4(), title="Sander", daily_rate=100, deposit=200, status="active",
    )
    block = ListingAvailabilityRecord.objects.create(
        listing=listing, start_date=date(2030, 5, 1), end_date=date(2030, 5, 3),
    )
    assert block.is_blocked is True
    assert list(listing.availability_blocks.values_list("id", flat=True)) == [block.id]


@pytest.mark.django_db(transaction=True)
def test_listing_availability_invalid_period_rejected_by_database():
    listing = ListingRecord.objects.create(
        owner_id=uuid4(), title="Sander", daily_rate=100, deposit=200, status="active",
    )
    with pytest.raises(IntegrityError), transaction.atomic():
        ListingAvailabilityRecord.objects.create(
            listing=listing, start_date=date(2030, 5, 3), end_date=date(2030, 5, 1),
        )
