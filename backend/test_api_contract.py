from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


print("=== TRUSTLENS API CONTRACT TEST ===")


fake_claims = [
    {"claim": "The Eiffel Tower is in Paris."},
    {"claim": "The Eiffel Tower is 500 meters tall."},
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
            "response": "Test response."
        }
    )


print("\nHTTP STATUS:")
print(response.status_code)

assert response.status_code == 200


result = response.json()

print("\nAPI RESPONSE:")
print(result)


print("\nCHECKING CONTRACT...")


# Top-level fields
assert "trust_score" in result
assert "total_claims" in result
assert "supported_claims" in result
assert "contradicted_claims" in result
assert "uncertain_claims" in result
assert "claims" in result

print("Top-level fields present ✅")


# Types
assert isinstance(result["trust_score"], (int, float))
assert isinstance(result["total_claims"], int)
assert isinstance(result["supported_claims"], int)
assert isinstance(result["contradicted_claims"], int)
assert isinstance(result["uncertain_claims"], int)
assert isinstance(result["claims"], list)

print("Top-level field types valid ✅")


# Claim structure
assert len(result["claims"]) == 2

claim = result["claims"][0]

required_claim_fields = [
    "claim",
    "verdict",
    "confidence",
    "reason",
    "evidence_quality",
    "relevant_sources",
    "evidence"
]

for field in required_claim_fields:
    assert field in claim

print("Claim fields present ✅")


# Claim field types
assert isinstance(claim["claim"], str)
assert isinstance(claim["verdict"], str)
assert isinstance(claim["confidence"], int)
assert isinstance(claim["reason"], str)
assert isinstance(claim["evidence_quality"], int)
assert isinstance(claim["relevant_sources"], list)
assert isinstance(claim["evidence"], list)

print("Claim field types valid ✅")


# Verdict validation
allowed_verdicts = {
    "SUPPORTED",
    "CONTRADICTED",
    "UNCERTAIN"
}

for item in result["claims"]:
    assert item["verdict"] in allowed_verdicts

print("Verdicts valid ✅")


# Trust score range
assert 0 <= result["trust_score"] <= 100

print("Trust score range valid ✅")


print("\nAPI contract test passed successfully! 🎉")
