from app.database import SessionLocal
from app.services.verification_repository import save_verification


print("=== TRUSTLENS VERIFICATION REPOSITORY TEST ===")


db = SessionLocal()

try:

    results = [
        {
            "claim": "The Eiffel Tower is in Paris.",
            "verdict": "SUPPORTED",
            "confidence": 100,
            "reason": "Evidence supports the claim.",
            "evidence_quality": 95,
        },
        {
            "claim": "The Eiffel Tower was completed in 1889.",
            "verdict": "SUPPORTED",
            "confidence": 100,
            "reason": "Evidence supports the claim.",
            "evidence_quality": 95,
        },
        {
            "claim": "The Eiffel Tower is 500 meters tall.",
            "verdict": "CONTRADICTED",
            "confidence": 98,
            "reason": "Evidence contradicts the claim.",
            "evidence_quality": 95,
        },
    ]

    verification = save_verification(
        db=db,
        original_response=(
            "The Eiffel Tower is in Paris. "
            "It was completed in 1889. "
            "It is 500 meters tall."
        ),
        trust_score=66.63,
        results=results
    )

    print("\nVerification saved ✅")
    print("Verification ID:", verification.id)


    # Verify values
    assert verification.trust_score == 66.63
    assert verification.total_claims == 3
    assert verification.supported_claims == 2
    assert verification.contradicted_claims == 1
    assert verification.uncertain_claims == 0

    print("Verification summary correct ✅")


    # Verify claims were saved
    claims = verification.claims

    assert len(claims) == 3

    assert claims[0].verdict == "SUPPORTED"
    assert claims[1].verdict == "SUPPORTED"
    assert claims[2].verdict == "CONTRADICTED"

    print("All claims saved correctly ✅")


finally:

    # Clean up test data
    if "verification" in locals() and verification.id:

        db.delete(verification)
        db.commit()

        print("Test verification deleted ✅")

    db.close()


print("\nAll verification repository tests passed successfully! 🎉")
