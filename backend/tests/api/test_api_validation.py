import pytest


def test_api_missing_response_body_authenticated_422(authenticated_client):
    response = authenticated_client.post("/api/verify", json={})
    assert response.status_code == 422


def test_api_empty_response_string_authenticated_422(authenticated_client):
    response = authenticated_client.post("/api/verify", json={"response": ""})
    assert response.status_code == 422


def test_api_oversized_response_string_authenticated_422(authenticated_client):
    response = authenticated_client.post("/api/verify", json={"response": "A" * 20001})
    assert response.status_code == 422


def test_api_invalid_payload_type_authenticated_422(authenticated_client):
    response = authenticated_client.post("/api/verify", json={"response": 12345})
    assert response.status_code == 422


def test_api_unauthenticated_invalid_payload_rejected_at_auth_layer_401(unauthenticated_client):
    """
    Ensure that unauthenticated requests fail with 401 at the authentication layer
    rather than leaking schema details through 422.
    """
    response = unauthenticated_client.post("/api/verify", json={})
    assert response.status_code == 401
    assert "Authorization header is required" in response.json()["detail"]
