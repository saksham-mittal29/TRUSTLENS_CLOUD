from unittest.mock import patch
import pytest


def test_api_partial_claim_failure_resilience(client):
    """
    Test that when one claim fails during verification (e.g. Gemini exception),
    it degrades gracefully to UNCERTAIN without failing the remaining claims or the overall HTTP request.
    """
    fake_claims = [
        {"claim": "Claim 1 is supported."},
        {"claim": "Claim 2 will raise an exception."},
        {"claim": "Claim 3 is supported."}
    ]

    fake_evidence = [
        {
            "title": "Test Source",
            "url": "https://example.com",
            "snippet": "Test evidence"
        }
    ]

    def mock_verify_claim(claim, evidence):
        if "Claim 2" in claim:
            raise RuntimeError("Simulated Gemini verification timeout/failure")
        return {
            "verdict": "SUPPORTED",
            "confidence": 95,
            "reason": "Verified successfully.",
            "evidence_quality": 90,
            "source_agreement": 90,
            "relevant_sources": [1]
        }

    with patch(
        "app.api.verification.extract_claims",
        return_value=fake_claims
    ), patch(
        "app.api.verification.search_evidence",
        return_value=fake_evidence
    ), patch(
        "app.api.verification.verify_claim",
        side_effect=mock_verify_claim
    ):
        response = client.post(
            "/api/verify",
            json={"response": "Test response with multiple claims."}
        )

    assert response.status_code == 200
    data = response.json()

    assert data["total_claims"] == 3
    assert data["supported_claims"] == 2
    assert data["contradicted_claims"] == 0
    assert data["uncertain_claims"] == 1

    assert data["claims"][0]["verdict"] == "SUPPORTED"
    assert data["claims"][1]["verdict"] == "UNCERTAIN"
    assert "Verification temporarily failed" in data["claims"][1]["reason"]
    assert data["claims"][2]["verdict"] == "SUPPORTED"
    assert 0 <= data["trust_score"] <= 100


def test_api_search_failure_resilience(client):
    """
    Test that when evidence search raises an exception, the system catches it,
    falls back to empty evidence, and marks the claim UNCERTAIN.
    """
    fake_claims = [{"claim": "Claim with broken search."}]

    def mock_search_fail(claim):
        raise ConnectionError("DuckDuckGo unreachable")

    with patch(
        "app.api.verification.extract_claims",
        return_value=fake_claims
    ), patch(
        "app.api.verification.search_evidence",
        side_effect=mock_search_fail
    ):
        response = client.post(
            "/api/verify",
            json={"response": "Test response with failing search."}
        )

    assert response.status_code == 200
    data = response.json()
    assert data["total_claims"] == 1
    assert data["uncertain_claims"] == 1
    assert data["claims"][0]["verdict"] == "UNCERTAIN"
