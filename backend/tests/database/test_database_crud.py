import pytest
from app.models import User, Verification, Claim


def test_user_verification_claim_crud(db_session):
    # 1. Create User
    user = User(firebase_uid="pytest-test-user-uid")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    assert user.id is not None

    try:
        # 2. Create Verification
        verification = Verification(
            user_id=user.id,
            original_response="Paris is the capital of France.",
            trust_score=95.0,
            total_claims=1,
            supported_claims=1,
            contradicted_claims=0,
            uncertain_claims=0
        )
        db_session.add(verification)
        db_session.commit()
        db_session.refresh(verification)
        assert verification.id is not None

        # 3. Create Claim
        claim = Claim(
            verification_id=verification.id,
            claim_text="Paris is the capital of France.",
            verdict="SUPPORTED",
            confidence=95,
            reason="Verified by geographic data.",
            evidence_quality=90
        )
        db_session.add(claim)
        db_session.commit()
        db_session.refresh(claim)
        assert claim.id is not None

        # 4. Query & Assert Relationships
        saved_verification = db_session.query(Verification).filter_by(id=verification.id).first()
        assert saved_verification is not None
        assert saved_verification.user.id == user.id
        assert len(saved_verification.claims) == 1
        assert saved_verification.claims[0].verdict == "SUPPORTED"

    finally:
        # Cleanup
        db_session.query(Claim).filter(Claim.verification_id == verification.id).delete()
        db_session.query(Verification).filter(Verification.id == verification.id).delete()
        db_session.query(User).filter(User.id == user.id).delete()
        db_session.commit()
