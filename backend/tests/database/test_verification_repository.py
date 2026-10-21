import pytest
from app.services.verification_repository import save_verification
from app.models import Verification, Claim, Evidence


def test_save_verification_cascade_and_aggregates(db_session):
    results = [
        {
            "claim": "The Eiffel Tower is in Paris.",
            "verdict": "SUPPORTED",
            "confidence": 100,
            "reason": "Confirmed by Wikipedia.",
            "evidence_quality": 95,
            "evidence": [
                {
                    "title": "Eiffel Tower - Wikipedia",
                    "url": "https://en.wikipedia.org/wiki/Eiffel_Tower",
                    "snippet": "Located in Paris."
                }
            ]
        },
        {
            "claim": "The Eiffel Tower was completed in 1999.",
            "verdict": "CONTRADICTED",
            "confidence": 98,
            "reason": "Actually completed in 1889.",
            "evidence_quality": 90,
            "evidence": []
        }
    ]

    verification = save_verification(
        db=db_session,
        original_response="Response about Eiffel Tower.",
        trust_score=50.0,
        results=results,
        user_id=None
    )

    try:
        assert verification.id is not None
        assert verification.total_claims == 2
        assert verification.supported_claims == 1
        assert verification.contradicted_claims == 1
        assert verification.uncertain_claims == 0

        saved = db_session.query(Verification).filter_by(id=verification.id).first()
        assert len(saved.claims) == 2
        assert len(saved.claims[0].evidence) == 1
        assert saved.claims[0].evidence[0].title == "Eiffel Tower - Wikipedia"

    finally:
        db_session.delete(verification)
        db_session.commit()
