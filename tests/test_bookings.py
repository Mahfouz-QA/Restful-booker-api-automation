# tests/test_bookings.py

import pytest


@pytest.mark.smoke
def test_TC4_auto_booking_create_full_POS(client):
    """
    TC4_auto_booking_create_full_POS: Create a new booking with all required fields
    and optional 'additionalneeds', verifying 200 OK and payload persistence.
    """
    payload = {
        "firstname": "Mahmoud",
        "lastname": "QA",
        "totalprice": 250,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2026-11-15",
            "checkout": "2026-11-20"
        },
        "additionalneeds": "Late Checkout"
    }

    response = client.create_booking(payload)

    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"

    data = response.json()
    assert "bookingid" in data, f"Missing 'bookingid' in response: {data}"
    assert isinstance(data["bookingid"], int), "bookingid must be an integer"

    booking = data["booking"]
    assert booking["firstname"] == payload["firstname"]
    assert booking["lastname"] == payload["lastname"]
    assert booking["totalprice"] == payload["totalprice"]
    assert booking["depositpaid"] == payload["depositpaid"]
    assert booking["bookingdates"]["checkin"] == payload["bookingdates"]["checkin"]
    assert booking["bookingdates"]["checkout"] == payload["bookingdates"]["checkout"]
    assert booking["additionalneeds"] == payload["additionalneeds"]


@pytest.mark.regression
def test_TC5_auto_booking_create_min_POS(client):
    """
    TC5_auto_booking_create_min_POS: Create a new booking omitting the optional
    'additionalneeds' field to verify mandatory-only payload contract.
    """
    min_payload = {
        "firstname": "Sara",
        "lastname": "Tester",
        "totalprice": 120,
        "depositpaid": False,
        "bookingdates": {
            "checkin": "2026-12-01",
            "checkout": "2026-12-05"
        }
    }

    response = client.create_booking(min_payload)

    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"

    data = response.json()
    assert "bookingid" in data, f"Missing 'bookingid' in response: {data}"
    assert isinstance(data["bookingid"], int), "bookingid must be an integer"

    booking = data["booking"]
    assert booking["firstname"] == min_payload["firstname"]
    assert booking["lastname"] == min_payload["lastname"]
    assert booking["totalprice"] == min_payload["totalprice"]
    assert booking["depositpaid"] == min_payload["depositpaid"]
    assert booking["bookingdates"]["checkin"] == min_payload["bookingdates"]["checkin"]
    assert booking["bookingdates"]["checkout"] == min_payload["bookingdates"]["checkout"]


@pytest.mark.smoke
def test_TC6_auto_booking_get_id_POS(client, created_booking):
    """
    TC6_auto_booking_get_id_POS: Retrieve a newly created booking by its dynamic
    bookingid and verify the persisted JSON matches the submitted payload.
    """
    booking_id = created_booking["booking_id"]
    expected_payload = created_booking["payload"]

    response = client.get_booking_by_id(booking_id)

    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"

    actual_booking = response.json()
    assert actual_booking == expected_payload, (
        f"Retrieved booking {actual_booking} did not match expected {expected_payload}"
    )


@pytest.mark.regression
def test_TC7_auto_booking_contract_CON(client, created_booking):
    """
    TC7_auto_booking_contract_CON: Validate response Content-Type header,
    required top-level and nested keys, and strict data types on GET /booking/{id}.
    """
    booking_id = created_booking["booking_id"]

    response = client.get_booking_by_id(booking_id)

    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"

    # 1. Validate Content-Type header
    content_type = response.headers.get("Content-Type", "")
    assert "application/json" in content_type, f"Unexpected Content-Type: {content_type}"

    # 2. Validate required keys exist
    data = response.json()
    required_keys = {"firstname", "lastname", "totalprice", "depositpaid", "bookingdates", "additionalneeds"}
    assert required_keys.issubset(data.keys()), f"Missing required schema keys in {data.keys()}"
    assert {"checkin", "checkout"}.issubset(data["bookingdates"].keys()), "Missing bookingdates sub-keys"

    # 3. Validate strict field data types
    assert isinstance(data["firstname"], str), "firstname must be str"
    assert isinstance(data["lastname"], str), "lastname must be str"
    assert isinstance(data["totalprice"], int) and not isinstance(data["totalprice"], bool), "totalprice must be int"
    assert isinstance(data["depositpaid"], bool), "depositpaid must be bool"
    assert isinstance(data["bookingdates"], dict), "bookingdates must be dict"
    assert isinstance(data["bookingdates"]["checkin"], str), "checkin must be str"
    assert isinstance(data["bookingdates"]["checkout"], str), "checkout must be str"
    assert isinstance(data["additionalneeds"], str), "additionalneeds must be str"


@pytest.mark.regression
def test_TC8_auto_booking_list_all_POS(client, created_booking):
    """
    TC8_auto_booking_list_all_POS: Retrieve the list of all active booking IDs
    and verify it returns a non-empty list of {'bookingid': int} objects.
    """
    response = client.get_bookings()

    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"

    data = response.json()
    assert isinstance(data, list), f"Expected a JSON list, got {type(data)}"
    assert len(data) > 0, "Expected at least one booking in the list"
    assert "bookingid" in data[0], f"List items must contain 'bookingid': {data[0]}"
    assert isinstance(data[0]["bookingid"], int), "bookingid must be an integer"


@pytest.mark.regression
def test_TC9_auto_booking_filter_name_POS(client, created_booking):
    """
    TC9_auto_booking_filter_name_POS: Filter bookings by the newly created
    booking's firstname and lastname and verify its booking_id is in the results.
    """
    expected_id = created_booking["booking_id"]
    payload = created_booking["payload"]

    query_params = {
        "firstname": payload["firstname"],
        "lastname": payload["lastname"]
    }

    response = client.get_bookings(params=query_params)

    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"

    data = response.json()
    assert isinstance(data, list), f"Expected a JSON list, got {type(data)}"

    returned_ids = [item["bookingid"] for item in data]
    assert expected_id in returned_ids, (
        f"Newly created booking_id {expected_id} not found in filtered results: {returned_ids}"
    )


@pytest.mark.smoke
def test_TC10_auto_booking_put_cookie_POS(client, created_booking, auth_token):
    """
    TC10_auto_booking_put_cookie_POS: Full update of an existing booking using
    a valid Cookie: token=<token> header.
    """
    booking_id = created_booking["booking_id"]
    updated_payload = {
        "firstname": "MahmoudUpdated",
        "lastname": "LeadQAUpdated",
        "totalprice": 550,
        "depositpaid": False,
        "bookingdates": {
            "checkin": "2026-12-10",
            "checkout": "2026-12-20"
        },
        "additionalneeds": "VIP Lounge"
    }

    response = client.update_booking(booking_id, updated_payload, token=auth_token)

    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
    assert response.json() == updated_payload, (
        f"Updated booking {response.json()} did not match {updated_payload}"
    )


@pytest.mark.regression
def test_TC11_auto_booking_put_basic_auth_POS(client, created_booking):
    """
    TC11_auto_booking_put_basic_auth_POS: Full update of an existing booking
    using the alternative Authorization: Basic header.
    """
    booking_id = created_booking["booking_id"]
    updated_payload = {
        "firstname": "BasicAuthUser",
        "lastname": "Tested",
        "totalprice": 400,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2026-12-15",
            "checkout": "2026-12-25"
        },
        "additionalneeds": "Early Check-in"
    }
    basic_auth_value = "Basic YWRtaW46cGFzc3dvcmQxMjM="

    response = client.update_booking(booking_id, updated_payload, auth_header=basic_auth_value)

    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
    assert response.json() == updated_payload


@pytest.mark.regression
def test_TC12_auto_booking_patch_POS(client, created_booking, auth_token):
    """
    TC12_auto_booking_patch_POS: Partial update of 'firstname' and 'additionalneeds'
    only, verifying untouched fields remain unchanged.
    """
    booking_id = created_booking["booking_id"]
    original_payload = created_booking["payload"]

    patch_payload = {
        "firstname": "PatchedName",
        "additionalneeds": "Extra Pillows"
    }

    response = client.partial_update_booking(booking_id, patch_payload, token=auth_token)

    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"

    expected_booking = {**original_payload, **patch_payload}
    assert response.json() == expected_booking, (
        f"PATCH corrupted untouched fields! Got {response.json()}, expected {expected_booking}"
    )


@pytest.mark.smoke
def test_TC13_auto_booking_delete_POS(client, created_booking, auth_token):
    """
    TC13_auto_booking_delete_POS: Delete an existing booking with a valid token
    and verify that a subsequent GET /booking/{id} returns 404 Not Found.
    """
    booking_id = created_booking["booking_id"]

    delete_response = client.delete_booking(booking_id, token=auth_token)
    assert delete_response.status_code == 201, (
        f"Expected status 201 on DELETE, got {delete_response.status_code}"
    )

    get_response = client.get_booking_by_id(booking_id)
    assert get_response.status_code == 404, (
        f"Deleted booking {booking_id} still exists! Expected 404, got {get_response.status_code}"
    )


@pytest.mark.smoke
def test_TC14_auto_booking_lifecycle_E2E(client, auth_token):
    """
    TC14_auto_booking_lifecycle_E2E: End-to-end booking lifecycle chain:
    POST (Create) -> GET (Verify Create) -> PUT (Update) -> GET (Verify Update) -> DELETE -> GET (Verify 404).
    """
    # 1. POST: Create a new booking
    initial_payload = {
        "firstname": "Lifecycle",
        "lastname": "Journey",
        "totalprice": 180,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2026-11-01",
            "checkout": "2026-11-05"
        },
        "additionalneeds": "None"
    }
    create_resp = client.create_booking(initial_payload)
    assert create_resp.status_code == 200
    booking_id = create_resp.json()["bookingid"]

    # 2. GET: Verify initial persistence
    get_initial_resp = client.get_booking_by_id(booking_id)
    assert get_initial_resp.status_code == 200
    assert get_initial_resp.json() == initial_payload

    # 3. PUT: Full update of the booking
    updated_payload = {
        "firstname": "Lifecycle",
        "lastname": "Completed",
        "totalprice": 320,
        "depositpaid": False,
        "bookingdates": {
            "checkin": "2026-11-02",
            "checkout": "2026-11-08"
        },
        "additionalneeds": "Airport Pickup"
    }
    put_resp = client.update_booking(booking_id, updated_payload, token=auth_token)
    assert put_resp.status_code == 200
    assert put_resp.json() == updated_payload

    # 4. GET: Verify updated state persisted in database
    get_updated_resp = client.get_booking_by_id(booking_id)
    assert get_updated_resp.status_code == 200
    assert get_updated_resp.json() == updated_payload

    # 5. DELETE: Remove the booking
    del_resp = client.delete_booking(booking_id, token=auth_token)
    assert del_resp.status_code == 201

    # 6. GET: Confirm deletion returns 404 Not Found
    get_deleted_resp = client.get_booking_by_id(booking_id)
    assert get_deleted_resp.status_code == 404


@pytest.mark.regression
@pytest.mark.parametrize("bad_token", [None, "invalid_token_123"])
def test_TC15_auto_booking_put_unauth_NEG(client, created_booking, bad_token):
    """
    TC15_auto_booking_put_unauth_NEG: Verify that full update (PUT) is blocked
    with 403 Forbidden when token is missing (None) or invalid, and record is unchanged.
    """
    booking_id = created_booking["booking_id"]
    original_payload = created_booking["payload"]

    tampered_payload = {
        "firstname": "Hacker",
        "lastname": "Tampered",
        "totalprice": 1,
        "depositpaid": False,
        "bookingdates": {
            "checkin": "2026-12-01",
            "checkout": "2026-12-02"
        },
        "additionalneeds": "Free Room"
    }

    response = client.update_booking(booking_id, tampered_payload, token=bad_token)
    assert response.status_code == 403, f"Expected 403 Forbidden, got {response.status_code}"

    get_resp = client.get_booking_by_id(booking_id)
    assert get_resp.status_code == 200
    assert get_resp.json() == original_payload, "Security defect: Unauthorized PUT modified the booking!"


@pytest.mark.regression
@pytest.mark.parametrize("bad_token", [None, "invalid_token_123"])
def test_TC16_auto_booking_patch_unauth_NEG(client, created_booking, bad_token):
    """
    TC16_auto_booking_patch_unauth_NEG: Verify that partial update (PATCH) is blocked
    with 403 Forbidden when token is missing (None) or invalid.
    """
    booking_id = created_booking["booking_id"]
    original_payload = created_booking["payload"]

    response = client.partial_update_booking(
        booking_id, {"firstname": "HackerPatch"}, token=bad_token
    )
    assert response.status_code == 403, f"Expected 403 Forbidden, got {response.status_code}"

    get_resp = client.get_booking_by_id(booking_id)
    assert get_resp.json() == original_payload


@pytest.mark.regression
@pytest.mark.parametrize("bad_token", [None, "invalid_token_123"])
def test_TC17_auto_booking_delete_unauth_NEG(client, created_booking, bad_token):
    """
    TC17_auto_booking_delete_unauth_NEG: Verify that booking deletion (DELETE) is blocked
    with 403 Forbidden when token is missing or invalid, and record still exists.
    """
    booking_id = created_booking["booking_id"]

    response = client.delete_booking(booking_id, token=bad_token)
    assert response.status_code == 403, f"Expected 403 Forbidden, got {response.status_code}"

    get_resp = client.get_booking_by_id(booking_id)
    assert get_resp.status_code == 200, "Security defect: Unauthorized DELETE removed the booking!"


@pytest.mark.regression
@pytest.mark.parametrize("invalid_id", [99999999, "invalid_id"])
def test_TC18_auto_booking_get_invalid_id_NEG(client, invalid_id):
    """
    TC18_auto_booking_get_invalid_id_NEG: Request a nonexistent booking ID (99999999)
    and a non-integer ID ('invalid_id') and verify 404 Not Found.
    """
    response = client.get_booking_by_id(invalid_id)
    assert response.status_code == 404, f"Expected 404 Not Found for ID {invalid_id}, got {response.status_code}"


@pytest.mark.regression
@pytest.mark.parametrize(
    "missing_field",
    ["firstname", "lastname", "totalprice", "depositpaid", "bookingdates"]
)
def test_TC19_auto_booking_create_missing_fields_NEG(client, missing_field):
    """
    TC19_auto_booking_create_missing_fields_NEG: Omit each of the 5 mandatory fields
    one by one on POST /booking and verify the server rejects the payload.
    (Note: RESTful Booker returns 500 Internal Server Error instead of 400 Bad Request).
    """
    payload = {
        "firstname": "Mahmoud",
        "lastname": "QA",
        "totalprice": 200,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2026-11-15",
            "checkout": "2026-11-20"
        },
        "additionalneeds": "Breakfast"
    }
    # Remove the target mandatory field before sending
    payload.pop(missing_field)

    response = client.create_booking(payload)
    assert response.status_code == 500, (
        f"Expected 500 error when missing '{missing_field}', got {response.status_code}"
    )


@pytest.mark.regression
def test_TC20_auto_booking_create_empty_body_NEG(client):
    """
    TC20_auto_booking_create_empty_body_NEG: Send an empty JSON object {} to POST /booking
    and verify the server rejects it with 500 Internal Server Error.
    """
    response = client.create_booking({})
    assert response.status_code == 500, f"Expected 500 on empty body, got {response.status_code}"


@pytest.mark.regression
def test_TC21_auto_booking_put_missing_field_NEG(client, created_booking, auth_token):
    """
    TC21_auto_booking_put_missing_field_NEG: Send an authenticated PUT /booking/{id}
    missing the mandatory 'firstname' field and verify 400 Bad Request.
    """
    booking_id = created_booking["booking_id"]
    incomplete_payload = {
        "lastname": "MissingFirstName",
        "totalprice": 300,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2026-12-01",
            "checkout": "2026-12-05"
        },
        "additionalneeds": "None"
    }

    response = client.update_booking(booking_id, incomplete_payload, token=auth_token)
    assert response.status_code == 400, f"Expected 400 Bad Request, got {response.status_code}"


@pytest.mark.regression
def test_TC22_auto_booking_accept_header_NEG(client):
    """
    TC22_auto_booking_accept_header_NEG: Send POST /booking with an unsupported
    Accept: text/plain header and verify 418 I'm a teapot response.
    """
    payload = {
        "firstname": "Teapot",
        "lastname": "HeaderTest",
        "totalprice": 100,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2026-12-01",
            "checkout": "2026-12-02"
        }
    }
    bad_headers = {"Accept": "text/plain"}

    response = client.create_booking(payload, headers=bad_headers)
    assert response.status_code == 418, f"Expected 418 I'm a teapot, got {response.status_code}"