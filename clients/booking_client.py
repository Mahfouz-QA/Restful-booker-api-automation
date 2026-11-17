# clients/booking_client.py

import requests
from utils.config import BASE_URL, TIMEOUT


class BookingClient:
    def __init__(self):
        self.base_url = BASE_URL
        self.timeout = TIMEOUT

    def ping(self):
        """
        TC1_auto_ping_POS: Send a GET request to the /ping health check endpoint.
        Expected: 201 Created
        """
        url = f"{self.base_url}/ping"
        return requests.get(url, timeout=self.timeout)

    def get_token(self, username="admin", password="password123"):
        """
        TC2 & TC3: Request an authentication token from POST /auth.
        """
        url = f"{self.base_url}/auth"
        payload = {
            "username": username,
            "password": password
        }
        return requests.post(url, json=payload, timeout=self.timeout)

    def create_booking(self, payload, headers=None):
        """
        TC4, TC5, TC19, TC20 & TC22: Create a new booking via POST /booking.
        Expected: 200 OK with a generated integer 'bookingid' and 'booking' object.
        """
        url = f"{self.base_url}/booking"
        default_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if headers is not None:
            default_headers.update(headers)
        return requests.post(url, json=payload, headers=default_headers, timeout=self.timeout)

    def get_booking_by_id(self, booking_id):
        """
        TC6, TC7 & TC18: Retrieve a specific booking by ID via GET /booking/{id}.
        Expected: 200 OK with booking JSON (or 404 Not Found if nonexistent).
        """
        url = f"{self.base_url}/booking/{booking_id}"
        headers = {
            "Accept": "application/json"
        }
        return requests.get(url, headers=headers, timeout=self.timeout)

    def get_bookings(self, params=None):
        """
        TC8 & TC9: Retrieve all booking IDs or filter by query parameters via GET /booking.
        """
        url = f"{self.base_url}/booking"
        return requests.get(url, params=params, timeout=self.timeout)

    def update_booking(self, booking_id, payload, token=None, auth_header=None):
        """
        TC10, TC11, TC15 & TC21: Full update of an existing booking via PUT /booking/{id}.
        Supports either Cookie token auth or a custom Authorization header.
        """
        url = f"{self.base_url}/booking/{booking_id}"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if token is not None:
            headers["Cookie"] = f"token={token}"
        if auth_header is not None:
            headers["Authorization"] = auth_header

        return requests.put(url, json=payload, headers=headers, timeout=self.timeout)

    def partial_update_booking(self, booking_id, payload, token=None):
        """
        TC12 & TC16: Partial update of an existing booking via PATCH /booking/{id}.
        """
        url = f"{self.base_url}/booking/{booking_id}"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if token is not None:
            headers["Cookie"] = f"token={token}"

        return requests.patch(url, json=payload, headers=headers, timeout=self.timeout)

    def delete_booking(self, booking_id, token=None):
        """
        TC13, TC14 & TC17: Delete an existing booking via DELETE /booking/{id}.
        Expected: 201 Created (RESTful Booker quirk) when authorized, 403 when unauthorized.
        """
        url = f"{self.base_url}/booking/{booking_id}"
        headers = {
            "Content-Type": "application/json"
        }
        if token is not None:
            headers["Cookie"] = f"token={token}"

        return requests.delete(url, headers=headers, timeout=self.timeout)