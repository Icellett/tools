"""Security headers required by lab 5."""
from django.test import Client


def test_security_headers_on_health():
    response = Client().get("/health")
    assert response.status_code == 200
    assert response["X-Content-Type-Options"] == "nosniff"
    assert response["X-Frame-Options"] == "DENY"


def test_booking_api_responses_are_not_cached():
    # Even an invalid request must not be cached.
    response = Client().post("/api/bookings", data="{}", content_type="application/json")
    assert response["X-Content-Type-Options"] == "nosniff"
    assert response["X-Frame-Options"] == "DENY"
    assert "no-store" in response["Cache-Control"]
