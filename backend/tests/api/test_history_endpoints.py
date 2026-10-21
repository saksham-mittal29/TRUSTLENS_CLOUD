from unittest.mock import patch
import pytest


def test_get_history_and_detail_authenticated_flow(authenticated_client, sample_claims, sample_evidence, sample_verification_result):
    # 1. Create a verification via /api/verify
    with patch(
        "app.api.verification.extract_claims",
        return_value=sample_claims
    ), patch(
        "app.api.verification.search_evidence",
        return_value=sample_evidence
    ), patch(
        "app.api.verification.verify_claim",
        return_value=sample_verification_result
    ):
        verify_res = authenticated_client.post(
            "/api/verify",
            json={"response": "The Eiffel Tower is in Paris."}
        )

    assert verify_res.status_code == 200
    verification_id = verify_res.json()["verification_id"]

    # 2. Query history list
    history_res = authenticated_client.get("/api/verifications")
    assert history_res.status_code == 200
    history_data = history_res.json()
    assert "total" in history_data
    assert "verifications" in history_data
    assert any(item["id"] == verification_id for item in history_data["verifications"])

    # 3. Query detail for the created verification
    detail_res = authenticated_client.get(f"/api/verifications/{verification_id}")
    assert detail_res.status_code == 200
    detail_data = detail_res.json()
    assert detail_data["id"] == verification_id
    assert "claims" in detail_data
    assert len(detail_data["claims"]) == 2

    # 4. Non-existent verification returns 404
    missing_res = authenticated_client.get("/api/verifications/99999999")
    assert missing_res.status_code == 404


def test_get_history_unauthenticated_rejected_401(unauthenticated_client):
    response = unauthenticated_client.get("/api/verifications")
    assert response.status_code == 401
    assert "Authorization header is required" in response.json()["detail"]


def test_get_detail_unauthenticated_rejected_401(unauthenticated_client):
    response = unauthenticated_client.get("/api/verifications/1")
    assert response.status_code == 401
    assert "Authorization header is required" in response.json()["detail"]
