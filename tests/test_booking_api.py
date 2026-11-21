"""Integration tests need PostgreSQL, provided by CI service."""
import uuid
from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from tutberry.models import BookingRecord, ListingRecord


@pytest.mark.django_db
def test_authenticated_booking_and_overlap():
    user = User.objects.create_user(username="tenant", password="test-password")
    listing = ListingRecord.objects.create(
        owner_id=uuid.uuid4(), title="Drill", daily_rate=Decimal("500"), deposit=Decimal("2000"), status="active"
    )
    client = APIClient()
    assert client.post("/api/bookings", {}).status_code == 403
    client.force_authenticate(user=user)
    payload = {"listing_id": str(listing.id), "start_date": "2030-01-01", "end_date": "2030-01-03"}
    first = client.post("/api/bookings", payload, format="json")
    assert first.status_code == 201
    assert first.json()["total"] == "3500.00"
    assert BookingRecord.objects.count() == 1
    second = client.post("/api/bookings", payload, format="json")
    assert second.status_code == 400
    assert BookingRecord.objects.count() == 1
