"""Contract tests for the currently implemented booking endpoint."""
import uuid
from decimal import Decimal
from pathlib import Path

import pytest
import yaml
from django.contrib.auth.models import User
from jsonschema import Draft4Validator, FormatChecker
from rest_framework.test import APIClient

from tutberry.models import ListingRecord

SPEC = yaml.safe_load(
    (Path(__file__).resolve().parents[1] / "docs/api/openapi.yaml").read_text(encoding="utf-8")
)
OPERATION = SPEC["paths"]["/api/bookings"]["post"]


def schema_for(name):
    schemas = SPEC["components"]["schemas"]
    schema = schemas[name]
    if "$ref" in schema:
        return schema_for(schema["$ref"].split("/")[-1])
    return schema


def validate_response(response, status_code):
    documented = OPERATION["responses"][str(status_code)]
    media_type = "application/json" if status_code == 201 else "application/problem+json"
    assert media_type in documented["content"]
    assert response["Content-Type"].split(";")[0] == media_type
    name = documented["content"][media_type]["schema"]["$ref"].split("/")[-1]
    errors = list(Draft4Validator(schema_for(name), format_checker=FormatChecker()).iter_errors(response.json()))
    assert not errors, [str(error) for error in errors]


def test_openapi_structure_and_security():
    assert SPEC["openapi"].startswith("3.")
    assert "basicAuth" in SPEC["components"]["securitySchemes"]
    assert OPERATION["security"] == [{"basicAuth": []}]
    assert set(OPERATION["responses"]) >= {"201", "400", "401", "403", "404", "409"}
    assert set(schema_for("CreateBookingRequest")["required"]) == {"listing_id", "start_date", "end_date"}


@pytest.mark.django_db
def test_booking_contract_success_authentication_and_conflict():
    user = User.objects.create_user(username="contract-tenant", password="secret")
    listing = ListingRecord.objects.create(
        owner_id=uuid.uuid4(), title="Drill", daily_rate=Decimal(100),
        deposit=Decimal(250), status="active",
    )
    client = APIClient()
    unauthorized = client.post("/api/bookings", {}, format="json")
    assert unauthorized.status_code == 401
    validate_response(unauthorized, 401)
    client.force_authenticate(user=user)
    payload = {
        "listing_id": str(listing.id),
        "start_date": "2030-01-01",
        "end_date": "2030-01-02",
    }
    created = client.post("/api/bookings", payload, format="json")
    assert created.status_code == 201
    validate_response(created, 201)
    conflict = client.post("/api/bookings", payload, format="json")
    assert conflict.status_code == 409
    validate_response(conflict, 409)


@pytest.mark.django_db
def test_booking_contract_validation_missing_and_ownership():
    user = User.objects.create_user(username="contract-owner", password="secret")
    owner_id = uuid.uuid5(uuid.NAMESPACE_URL, f"tutberry:user:{user.pk}")
    listing = ListingRecord.objects.create(
        owner_id=owner_id, title="Saw", daily_rate=Decimal(100),
        deposit=Decimal(250), status="active",
    )
    client = APIClient()
    client.force_authenticate(user=user)
    invalid = client.post("/api/bookings", {"listing_id": "not-a-uuid"}, format="json")
    assert invalid.status_code == 400
    validate_response(invalid, 400)
    missing = client.post("/api/bookings", {
        "listing_id": str(uuid.uuid4()), "start_date": "2030-01-01",
        "end_date": "2030-01-02",
    }, format="json")
    assert missing.status_code == 404
    validate_response(missing, 404)
    forbidden = client.post("/api/bookings", {
        "listing_id": str(listing.id), "start_date": "2030-01-01",
        "end_date": "2030-01-02",
    }, format="json")
    assert forbidden.status_code == 403
    validate_response(forbidden, 403)
