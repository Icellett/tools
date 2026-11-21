"""Integration coverage of FR-01: search with real PostgreSQL."""
from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest
from rest_framework.test import APIClient

from tutberry.models import BookingRecord, ListingAvailabilityRecord, ListingRecord


@pytest.mark.django_db
def test_search_excludes_reserved_and_blocked_out_of_ten():
    entries = [
        ListingRecord.objects.create(
            owner_id=uuid4(), title=f"Drill {n}", category="drill",
            location="Omsk", daily_rate=Decimal(500), deposit=Decimal(100),
            status="active",
        )
        for n in range(10)
    ]
    BookingRecord.objects.create(
        listing=entries[0], tenant_id=uuid4(), start_date=date(2030, 6, 10),
        end_date=date(2030, 6, 12), rent=Decimal(1000),
        deposit=Decimal(100), status="approved",
    )
    url = "/api/listings?start_date=2030-06-12&end_date=2030-06-13"
    response = APIClient().get(url)
    assert response.status_code == 200
    assert len(response.json()["items"]) == 9
    assert str(entries[0].id) not in {item["id"] for item in response.json()["items"]}
    adjacent = APIClient().get("/api/listings?start_date=2030-06-13&end_date=2030-06-14")
    assert len(adjacent.json()["items"]) == 10
    ListingAvailabilityRecord.objects.create(
        listing=entries[1], start_date=date(2030, 6, 13),
        end_date=date(2030, 6, 14), is_blocked=True,
    )
    assert len(APIClient().get(url).json()["items"]) == 9


@pytest.mark.django_db
def test_search_filters_category_location_price_and_status():
    ListingRecord.objects.create(
        owner_id=uuid4(), title="Affordable Drill", category="drill",
        location="Omsk", daily_rate=Decimal(400), deposit=Decimal(200), status="active",
    )
    ListingRecord.objects.create(
        owner_id=uuid4(), title="Expensive Drill", category="drill",
        location="Omsk", daily_rate=Decimal(900), deposit=Decimal(100), status="active",
    )
    ListingRecord.objects.create(
        owner_id=uuid4(), title="Hidden Drill", category="drill",
        location="Omsk", daily_rate=Decimal(400), deposit=Decimal(0), status="draft",
    )
    ListingRecord.objects.create(
        owner_id=uuid4(), title="Saw", category="saw",
        location="Moscow", daily_rate=Decimal(400), deposit=Decimal(0), status="active",
    )
    response = APIClient().get("/api/listings", {
        "start_date": "2030-06-01", "end_date": "2030-06-02",
        "category": "DRILL", "location": "omsk", "max_price": "500",
        "min_price": "300",
    })
    assert response.status_code == 200
    assert [item["title"] for item in response.json()["items"]] == ["Affordable Drill"]


@pytest.mark.django_db
def test_search_invalid_inputs_and_pagination():
    client = APIClient()
    assert client.get("/api/listings").status_code == 400
    assert client.get("/api/listings?start_date=2030-06-02&end_date=2030-06-01").status_code == 400
    assert client.get("/api/listings?start_date=2030-06-01&end_date=2030-06-02&limit=101").status_code == 400
    assert client.get("/api/listings?start_date=2030-06-01&end_date=2030-06-02&min_price=200&max_price=100").status_code == 400
    for n in range(3):
        ListingRecord.objects.create(
            owner_id=uuid4(), title=f"Listing {n}", category="tool",
            location="Omsk", daily_rate=Decimal(10), deposit=Decimal(0), status="active",
        )
    response = client.get("/api/listings?start_date=2030-06-01&end_date=2030-06-02&limit=2")
    assert response.status_code == 200
    assert len(response.json()["items"]) == 2
