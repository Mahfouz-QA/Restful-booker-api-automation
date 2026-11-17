# tests/conftest.py

import pytest
from clients.booking_client import BookingClient


@pytest.fixture
def client():
    """Provides a fresh BookingClient instance for test functions."""
    return BookingClient()


@pytest.fixture
def auth_token(client):
    """
    Authenticates via POST /auth and returns a valid token string
    for protected PUT, PATCH, and DELETE operations.
    """
    response = client.get_token()
    assert response.status_code == 200, f"Auth fixture failed: {response.text}"
    token = response.json().get("token")
    assert token, f"Auth fixture did not receive a token: {response.json()}"
    return token


@pytest.fixture
def created_booking(client):
    """
    Creates a fresh booking before a test runs and returns its dynamic
    booking_id alongside the original payload for verification.
    """
    payload = {
        "firstname": "Mahmoud",
        "lastname": "LeadQA",
        "totalprice": 300,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2026-11-15",
            "checkout": "2026-11-22"
        },
        "additionalneeds": "Airport Shuttle"
    }
    response = client.create_booking(payload)
    assert response.status_code == 200, f"Fixture setup failed to create booking: {response.text}"

    booking_id = response.json()["bookingid"]
    return {
        "booking_id": booking_id,
        "payload": payload
    }