# tests/test_ping.py

import pytest


@pytest.mark.smoke
def test_TC1_auto_ping_POS(client):
    """
    TC1_auto_ping_POS: Verify that the RESTful Booker API server is online
    and responds within 2000ms.
    """
    response = client.ping()

    assert response.status_code == 201, f"Expected status code 201, got {response.status_code}"
    assert response.elapsed.total_seconds() < 2.0, "Health check took longer than 2000ms"