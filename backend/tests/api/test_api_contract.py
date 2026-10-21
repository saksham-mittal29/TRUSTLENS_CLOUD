from unittest.mock import patch
import pytest


def test_verify_endpoint_contract_authenticated(authenticated_client, sample_claims, sample_evidence, sample_verification_result):
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
        response = authenticated_client.post(
            "/api/verify",
            json={"response": "The Eiffel Tower is in Paris. It was completed in 1889."}
        )

    assert response.status_code == 200
    data = response.json()

    # Top-level contract validation
    for field in ["verification_id", "trust_score", "total_claims", "supported_claims", "contradicted_claims", "uncertain_claims", "claims"]:
        assert field in data

    assert isinstance(data["verification_id"], int)
    assert isinstance(data["trust_score"], (int, float))
    assert data["total_claims"] == 2
    assert data["supported_claims"] == 2
    assert data["contradicted_claims"] == 0
    assert data["uncertain_claims"] == 0
    assert isinstance(data["claims"], list)
    assert len(data["claims"]) == 2

    # Claim object structure validation
    claim = data["claims"][0]
    for key in ["claim", "verdict", "confidence", "reason", "evidence_quality", "relevant_sources", "evidence"]:
        assert key in claim

    assert claim["verdict"] in {"SUPPORTED", "CONTRADICTED", "UNCERTAIN"}
    assert 0 <= data["trust_score"] <= 100


def test_verify_endpoint_unauthenticated_missing_header_rejected(unauthenticated_client):
    response = unauthenticated_client.post(
        "/api/verify",
        json={"response": "The Eiffel Tower is in Paris."}
    )
    assert response.status_code == 401
    assert "Authorization header is required" in response.json()["detail"]


def test_verify_endpoint_unauthenticated_invalid_scheme_rejected(unauthenticated_client):
    response = unauthenticated_client.post(
        "/api/verify",
        json={"response": "The Eiffel Tower is in Paris."},
        headers={"Authorization": "Basic invalid_credentials"}
    )
    assert response.status_code == 401
    assert "must use Bearer token" in response.json()["detail"]


def test_verify_endpoint_unauthenticated_empty_token_rejected(unauthenticated_client):
    response = unauthenticated_client.post(
        "/api/verify",
        json={"response": "The Eiffel Tower is in Paris."},
        headers={"Authorization": "Bearer "}
    )
    assert response.status_code == 401
    assert "Firebase ID token is required" in response.json()["detail"]
