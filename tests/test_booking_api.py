"""Integration tests need PostgreSQL, provided by CI service."""
import uuid
from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from tutberry.models import BookingRecord, ListingAvailabilityRecord, ListingRecord


@pytest.mark.django_db
def test_authenticated_booking_and_overlap():
    user = User.objects.create_user(username="tenant", password="test-password")
    listing = ListingRecord.objects.create(
        owner_id=uuid.uuid4(), title="Drill", daily_rate=Decimal("500"), deposit=Decimal("2000"), status="active"
    )
    client = APIClient()
    unauthorized = client.post("/api/bookings", {})
    assert unauthorized.status_code == 401
    assert unauthorized.json()["status"] == 401
    client.force_authenticate(user=user)
    payload = {"listing_id": str(listing.id), "start_date": "2030-01-01", "end_date": "2030-01-03"}
    first = client.post("/api/bookings", payload, format="json")
    assert first.status_code == 201
    assert first.json()["total"] == "3500.00"
    assert BookingRecord.objects.count() == 1
    second = client.post("/api/bookings", payload, format="json")
    assert second.status_code == 409
    assert second.json()["title"] == "Conflict"
    assert BookingRecord.objects.count() == 1


@pytest.mark.django_db
def test_validation_and_owner_permission_problem_details():
    user = User.objects.create_user(username="owner", password="test-password")
    owner_uuid = uuid.uuid5(uuid.NAMESPACE_URL, f"tutberry:user:{user.pk}")
    listing = ListingRecord.objects.create(
        owner_id=owner_uuid, title="Saw", daily_rate=Decimal("300"),
        deposit=Decimal("1000"), status="active",
    )
    client = APIClient()
    client.force_authenticate(user=user)
    invalid = client.post("/api/bookings", {"listing_id": "not-a-uuid"}, format="json")
    assert invalid.status_code == 400
    assert invalid.json()["status"] == 400
    assert "errors" in invalid.json()
    own = client.post("/api/bookings", {
        "listing_id": str(listing.id), "start_date": "2030-03-01",
        "end_date": "2030-03-02",
    }, format="json")
    assert own.status_code == 403
    assert own.json()["title"] == "Forbidden"


@pytest.mark.django_db
def test_owner_calendar_block_rejects_overlapping_booking_but_allows_adjacent_dates():
    user = User.objects.create_user(username="calendar-tenant", password="test-password")
    listing = ListingRecord.objects.create(
        owner_id=uuid.uuid4(), title="Router", daily_rate=Decimal("100"),
        deposit=Decimal("200"), status="active",
    )
    ListingAvailabilityRecord.objects.create(
        listing=listing, start_date=date(2030, 6, 10), end_date=date(2030, 6, 12),
        is_blocked=True,
    )
    ListingAvailabilityRecord.objects.create(
        listing=listing, start_date=date(2030, 6, 20), end_date=date(2030, 6, 21),
        is_blocked=False,
    )
    client = APIClient()
    client.force_authenticate(user=user)
    def post(start, end):
        return client.post("/api/bookings", {
            "listing_id": str(listing.id), "start_date": start, "end_date": end,
        }, format="json")

    blocked = post("2030-06-12", "2030-06-13")
    assert blocked.status_code == 409
    assert blocked.json()["title"] == "Conflict"
    assert BookingRecord.objects.count() == 0

    adjacent = post("2030-06-13", "2030-06-14")
    assert adjacent.status_code == 201
    unblocked = post("2030-06-20", "2030-06-21")
    assert unblocked.status_code == 201
    assert BookingRecord.objects.count() == 2
