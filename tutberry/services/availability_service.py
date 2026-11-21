"""Owner calendar writes serialized against booking creation.

Both operations acquire the same ListingRecord row lock. Callers must use
this function for calendar mutations; direct ORM writes bypass this protocol.
"""
from django.db import transaction

from tutberry.models import BookingRecord, ListingAvailabilityRecord, ListingRecord


class AvailabilityConflict(ValueError):
    pass


@transaction.atomic
def set_listing_block(*, listing_id, owner_id, start_date, end_date, is_blocked=True):
    if end_date < start_date:
        raise ValueError("End date must not precede start date")
    listing = ListingRecord.objects.select_for_update().get(id=listing_id, owner_id=owner_id)
    if is_blocked and BookingRecord.objects.filter(
        listing=listing,
        start_date__lte=end_date,
        end_date__gte=start_date,
    ).exclude(status="cancelled").exists():
        raise AvailabilityConflict("An active booking overlaps the requested block")
    return ListingAvailabilityRecord.objects.create(
        listing=listing, start_date=start_date, end_date=end_date, is_blocked=is_blocked,
    )
