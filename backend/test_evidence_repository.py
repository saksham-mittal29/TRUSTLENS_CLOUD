from app.database import SessionLocal
from app.services.verification_repository import save_verification


db = SessionLocal()

try:
    results = [
        {
            "claim": "The Eiffel Tower is in Paris.",
            "verdict": "SUPPORTED",
            "confidence": 100,
            "reason": "Multiple sources confirm that the Eiffel Tower is located in Paris.",
            "evidence_quality": 95,
            "evidence": [
                {
                    "title": "Eiffel Tower - Wikipedia",
                    "url": "https://en.wikipedia.org/wiki/Eiffel_Tower",
                    "snippet": "The Eiffel Tower is a landmark in Paris."
                },
                {
                    "title": "Official Eiffel Tower Website",
                    "url": "https://www.toureiffel.paris/en",
                    "snippet": "The Eiffel Tower is located in Paris."
                }
            ]
        }
    ]

    verification = save_verification(
        db=db,
        original_response="The Eiffel Tower is in Paris.",
        trust_score=98.5,
        results=results,
        user_id=None
    )

    print("Verification saved:", verification.id)
    print("Claims saved:", len(verification.claims))

    claim = verification.claims[0]

    print("Claim saved:", claim.claim_text)
    print("Evidence saved:", len(claim.evidence))

    for evidence in claim.evidence:
        print(" -", evidence.title)
        print("   ", evidence.url)

finally:
    db.close()
