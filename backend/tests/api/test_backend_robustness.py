from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_current_firebase_user
from app.database import get_db
from app.main import app
from app.models import User, Verification


@pytest.fixture
def mock_db():
    """
    Mock SQLAlchemy database session that does not require a live PostgreSQL database.
    """
    session = MagicMock()
    
    def mock_query(model):
        query_mock = MagicMock()
        if model == User or getattr(model, "__tablename__", "") == "users":
            mock_user = MagicMock()
            mock_user.id = 42
            mock_user.firebase_uid = "mock-firebase-uid"
            query_mock.filter.return_value.first.return_value = mock_user
        else:
            mock_source = MagicMock()
            mock_source.historical_reliability = 50.0
            query_mock.filter.return_value.first.return_value = mock_source
        return query_mock

    session.query.side_effect = mock_query
    return session



@pytest.fixture
def mock_client(mock_db, mock_firebase_user):
    """
    TestClient with both database session and Firebase auth injected via FastAPI dependency_overrides.
    """
    app.dependency_overrides[get_current_firebase_user] = lambda: mock_firebase_user
    app.dependency_overrides[get_db] = lambda: mock_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_four_scenario_claim_pipeline_robustness(mock_client, mock_db):
    """
    Validates the original test_backend_robustness.py scenarios across 4 claims:
    1. Claim 1: SUPPORTED
    2. Claim 2: CONTRADICTED
    3. Claim 3: Zero evidence retrieved -> UNCERTAIN fallback
    4. Claim 4: Gemini verification failure/exception -> UNCERTAIN fallback
    """
    fake_claims = [
        {"claim": "Claim one is supported."},
        {"claim": "Claim two is contradicted."},
        {"claim": "Claim three has no evidence."},
        {"claim": "Claim four triggers a verifier exception."}
    ]

    def mock_search_evidence(claim):
        if "Claim three" in claim:
            return []
        return [
            {
                "title": "Test Source",
                "url": "https://example.com/source",
                "snippet": "Evidence for testing."
            }
        ]

    def mock_verify_claim(claim, evidence):
        if "Claim four" in claim:
            raise RuntimeError("Simulated Gemini API 500 error or timeout")
        if "Claim two" in claim:
            return {
                "verdict": "CONTRADICTED",
                "confidence": 95,
                "reason": "Evidence refutes the claim.",
                "evidence_quality": 90,
                "relevant_sources": [1]
            }
        if "Claim three" in claim:
            # Should not be called if evidence is empty because verify_claim handles it
            return {
                "verdict": "UNCERTAIN",
                "confidence": 0,
                "reason": "No evidence was found.",
                "evidence_quality": 0,
                "relevant_sources": []
            }
        # Claim one is supported
        return {
            "verdict": "SUPPORTED",
            "confidence": 95,
            "reason": "Evidence confirms the claim.",
            "evidence_quality": 90,
            "relevant_sources": [1]
        }

    mock_saved_verification = MagicMock(spec=Verification)
    mock_saved_verification.id = 999

    with patch(
        "app.api.verification.extract_claims",
        return_value=fake_claims
    ), patch(
        "app.api.verification.search_evidence",
        side_effect=mock_search_evidence
    ), patch(
        "app.api.verification.verify_claim",
        side_effect=mock_verify_claim
    ), patch(
        "app.api.verification.save_verification",
        return_value=mock_saved_verification
    ), patch(
        "app.api.verification.get_or_create_user",
        return_value=MagicMock(id=1, firebase_uid="mock-uid")
    ), patch(
        "app.api.verification.get_historical_reliability",
        return_value=50.0
    ), patch(
        "app.api.verification.update_source_reliability"
    ):
        response = mock_client.post(
            "/api/verify",
            json={"response": "Test response containing four different claims."}
        )

    assert response.status_code == 200
    data = response.json()

    # Response overview checks
    assert data["total_claims"] == 4
    assert data["supported_claims"] == 1
    assert data["contradicted_claims"] == 1
    assert data["uncertain_claims"] == 2
    assert 0 <= data["trust_score"] <= 100

    # Claim 1: SUPPORTED
    assert data["claims"][0]["verdict"] == "SUPPORTED"
    assert data["claims"][0]["confidence"] == 95

    # Claim 2: CONTRADICTED
    assert data["claims"][1]["verdict"] == "CONTRADICTED"
    assert data["claims"][1]["confidence"] == 95

    # Claim 3: Empty evidence -> UNCERTAIN
    assert data["claims"][2]["verdict"] == "UNCERTAIN"
    assert data["claims"][2]["confidence"] == 0
    assert data["claims"][2]["evidence_quality"] == 0
    assert data["claims"][2]["relevant_sources"] == []

    # Claim 4: Exception -> UNCERTAIN fallback
    assert data["claims"][3]["verdict"] == "UNCERTAIN"
    assert data["claims"][3]["confidence"] == 0
    assert "Verification temporarily failed" in data["claims"][3]["reason"]


def test_claim_extraction_gemini_quota_error_429(mock_client):
    with patch(
        "app.api.verification.extract_claims",
        side_effect=Exception("429 RESOURCE_EXHAUSTED quota exceeded")
    ):
        response = mock_client.post(
            "/api/verify",
            json={"response": "Some response text."}
        )

    assert response.status_code == 429
    assert "Gemini API quota exceeded" in response.json()["detail"]


def test_claim_extraction_gemini_unavailable_error_503(mock_client):
    with patch(
        "app.api.verification.extract_claims",
        side_effect=Exception("503 UNAVAILABLE service down")
    ):
        response = mock_client.post(
            "/api/verify",
            json={"response": "Some response text."}
        )

    assert response.status_code == 503
    assert "temporarily unavailable" in response.json()["detail"]


def test_database_persistence_error_triggers_rollback_and_500(mock_client, mock_db, sample_claims, sample_evidence, sample_verification_result):
    with patch(
        "app.api.verification.extract_claims",
        return_value=sample_claims
    ), patch(
        "app.api.verification.search_evidence",
        return_value=sample_evidence
    ), patch(
        "app.api.verification.verify_claim",
        return_value=sample_verification_result
    ), patch(
        "app.api.verification.save_verification",
        side_effect=RuntimeError("Database connection lost")
    ), patch(
        "app.api.verification.get_or_create_user",
        return_value=MagicMock(id=1)
    ):
        response = mock_client.post(
            "/api/verify",
            json={"response": "Test response."}
        )

    assert response.status_code == 500
    assert "Failed to save verification" in response.json()["detail"]
    mock_db.rollback.assert_called_once()
