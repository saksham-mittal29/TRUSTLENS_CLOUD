from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import text

from app.database import SessionLocal
from app.main import app


client = TestClient(app)


print("=== TRUSTLENS API + DATABASE INTEGRATION TEST ===")


fake_claims = [
    {"claim": "The Eiffel Tower is in Paris."},
    {"claim": "The Eiffel Tower was completed in 1889."},
]


fake_evidence = [
    {
        "title": "Test Source",
        "url": "https://example.com",
        "snippet": "Test evidence"
    }
]


fake_verification = {
    "verdict": "SUPPORTED",
    "confidence": 95,
    "reason": "Evidence supports the claim.",
    "evidence_quality": 90,
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
    return_value=fake_verification
):

    response = client.post(
        "/api/verify",
        json={
            "response": "Test response for database integration."
        }
    )


print("\nHTTP STATUS:")
print(response.status_code)

assert response.status_code == 200

result = response.json()

print("\nAPI RESPONSE:")
print(result)


# Check verification ID
assert "verification_id" in result
assert isinstance(result["verification_id"], int)

print("\nVerification ID returned ✅")


# Check response contract
assert result["total_claims"] == 2
assert result["supported_claims"] == 2
assert result["contradicted_claims"] == 0
assert result["uncertain_claims"] == 0

print("API response contract preserved ✅")


# Check database
db = SessionLocal()

try:

    verification_id = result["verification_id"]

    verification_row = db.execute(
        text(
            """
            SELECT
                id,
                original_response,
                trust_score,
                total_claims,
                supported_claims,
                contradicted_claims,
                uncertain_claims
            FROM verifications
            WHERE id = :verification_id
            """
        ),
        {
            "verification_id": verification_id
        }
    ).mappings().first()

    assert verification_row is not None

    assert verification_row["original_response"] == (
        "Test response for database integration."
    )

    assert verification_row["trust_score"] == 93.5
    assert verification_row["total_claims"] == 2
    assert verification_row["supported_claims"] == 2

    print("Verification saved to PostgreSQL ✅")


    claim_count = db.execute(
        text(
            """
            SELECT COUNT(*)
            FROM claims
            WHERE verification_id = :verification_id
            """
        ),
        {
            "verification_id": verification_id
        }
    ).scalar()

    assert claim_count == 2

    print("Claims saved to PostgreSQL ✅")


finally:

    # Clean up integration test data
    db.execute(
        text(
            """
            DELETE FROM claims
            WHERE verification_id = :verification_id
            """
        ),
        {
            "verification_id": result["verification_id"]
        }
    )

    db.execute(
        text(
            """
            DELETE FROM verifications
            WHERE id = :verification_id
            """
        ),
        {
            "verification_id": result["verification_id"]
        }
    )

    db.commit()
    db.close()

    print("Test database records cleaned up ✅")


print("\nAPI + database integration test passed successfully! 🎉")
