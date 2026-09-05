from app.database import SessionLocal
from app.models import User, Verification, Claim


print("=== TRUSTLENS DATABASE CRUD TEST ===")


db = SessionLocal()

try:
    # 1. Create a test user
    user = User(
        firebase_uid="test-firebase-user"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    print("\nTest 1: User created ✅")
    print("User ID:", user.id)


    # 2. Create a verification
    verification = Verification(
        user_id=user.id,
        original_response="The Eiffel Tower is in Paris.",
        trust_score=93.5,
        total_claims=1,
        supported_claims=1,
        contradicted_claims=0,
        uncertain_claims=0
    )

    db.add(verification)
    db.commit()
    db.refresh(verification)

    print("Test 2: Verification created ✅")
    print("Verification ID:", verification.id)


    # 3. Create a claim
    claim = Claim(
        verification_id=verification.id,
        claim_text="The Eiffel Tower is in Paris.",
        verdict="SUPPORTED",
        confidence=95,
        reason="Evidence supports the claim.",
        evidence_quality=90
    )

    db.add(claim)
    db.commit()
    db.refresh(claim)

    print("Test 3: Claim created ✅")
    print("Claim ID:", claim.id)


    # 4. Read verification and claims
    saved_verification = db.query(Verification).filter(
        Verification.id == verification.id
    ).first()

    assert saved_verification is not None
    assert saved_verification.trust_score == 93.5

    saved_claims = db.query(Claim).filter(
        Claim.verification_id == verification.id
    ).all()

    assert len(saved_claims) == 1
    assert saved_claims[0].verdict == "SUPPORTED"

    print("Test 4: Verification and claim read successfully ✅")


    # 5. Test relationships
    assert saved_verification.user.id == user.id
    assert saved_verification.claims[0].id == claim.id

    print("Test 5: SQLAlchemy relationships working ✅")


finally:
    # Remove test data
    if 'verification' in locals():
        db.query(Claim).filter(
            Claim.verification_id == verification.id
        ).delete()

        db.query(Verification).filter(
            Verification.id == verification.id
        ).delete()

    if 'user' in locals():
        db.query(User).filter(
            User.id == user.id
        ).delete()

    db.commit()
    db.close()


print("\nTest data cleaned up ✅")
print("\nAll database CRUD tests passed successfully! 🎉")