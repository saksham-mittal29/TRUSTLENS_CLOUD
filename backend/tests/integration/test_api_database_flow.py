from unittest.mock import patch
import pytest
from app.models import Verification, Claim, SourceReliability


def test_verify_api_to_database_persistence_flow_authenticated(authenticated_client, db_session, sample_claims, sample_evidence, sample_verification_result):
    """
    Test that an authenticated user calling POST /api/verify persists the verification,
    associated claims, and updates source reliability in PostgreSQL.
    """
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
    verification_id = data["verification_id"]

    try:
        # Check verification saved in database
        saved_verification = db_session.query(Verification).filter_by(id=verification_id).first()
        assert saved_verification is not None
        assert saved_verification.total_claims == 2
        assert saved_verification.supported_claims == 2
        assert saved_verification.trust_score == data["trust_score"]

        # Check claims saved
        claims = db_session.query(Claim).filter_by(verification_id=verification_id).all()
        assert len(claims) == 2
        assert claims[0].verdict == "SUPPORTED"

        # Check source reliability updated for en.wikipedia.org
        source_rel = db_session.query(SourceReliability).filter_by(domain="en.wikipedia.org").first()
        assert source_rel is not None
        assert source_rel.total_evaluations >= 1

    finally:
        # Cleanup
        db_session.delete(saved_verification)
        db_session.commit()


def test_verify_api_unauthenticated_does_not_persist_records(unauthenticated_client, db_session):
    """
    Ensure that an unauthenticated request is rejected with 401 and creates zero database records.
    """
    initial_count = db_session.query(Verification).count()

    response = unauthenticated_client.post(
        "/api/verify",
        json={"response": "Unauthenticated attempt to persist verification."}
    )

    assert response.status_code == 401
    final_count = db_session.query(Verification).count()
    assert final_count == initial_count
