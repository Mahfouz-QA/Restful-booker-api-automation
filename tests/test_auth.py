# tests/test_auth.py

import pytest


@pytest.mark.smoke
def test_TC2_auto_auth_valid_POS(client):
    """
    TC2_auto_auth_valid_POS: Verify that valid admin credentials return
    HTTP 200 and a non-empty authentication token.
    """
    response = client.get_token()

    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"

    data = response.json()
    assert "token" in data, f"Response JSON missing 'token' key: {data}"
    assert isinstance(data["token"], str), "Token must be a string"
    assert len(data["token"]) > 0, "Token string cannot be empty"


@pytest.mark.regression
@pytest.mark.parametrize(
    "username, password",
    [
        ("invalid_user", "password123"),  # Case 1: Wrong username, valid password
        ("admin", "wrong_password"),      # Case 2: Valid username, wrong password
        ("", ""),                         # Case 3: Empty username and password
    ],
)
def test_TC3_auto_auth_invalid_NEG(client, username, password):
    """
    TC3_auto_auth_invalid_NEG: Verify that invalid credentials do not return a token
    and instead return {"reason": "Bad credentials"}.
    """
    response = client.get_token(username=username, password=password)

    # RESTful Booker quirk: returns HTTP 200 even on failed auth, with a 'reason' field
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"

    data = response.json()
    assert "token" not in data, f"Security defect: Token was issued for bad credentials! {data}"
    assert data.get("reason") == "Bad credentials", f"Unexpected error message: {data}"