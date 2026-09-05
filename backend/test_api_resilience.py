from unittest.mock import patch

from app.api.verification import verify_response
from app.schemas.verification import VerificationRequest


# Fake claims returned by the claim extractor
fake_claims = [
    {"claim": "Claim one is true."},
    {"claim": "Claim two will fail verification."},
    {"claim": "Claim three is true."}
]


# Fake evidence returned by the evidence search
fake_evidence = [
    {
        "title": "Test Source",
        "url": "https://example.com",
        "snippet": "Test evidence"
    }
]


def fake_verify_claim(claim, evidence):

    # Deliberately fail the second claim
    if "Claim two" in claim:
        raise Exception("Simulated verification failure")

    return {
        "verdict": "SUPPORTED",
        "confidence": 95,
        "reason": "Test verification succeeded.",
        "evidence_quality": 90,
        "relevant_sources": [1]
    }


print("=== API RESILIENCE TEST ===")


request = VerificationRequest(
    response="Test response containing three claims."
)


with patch(
    "app.api.verification.extract_claims",
    return_value=fake_claims
), patch(
    "app.api.verification.search_evidence",
    return_value=fake_evidence
), patch(
    "app.api.verification.verify_claim",
    side_effect=fake_verify_claim
):

    result = verify_response(request)


print("\nAPI RESULT:")
print(result)


print("\nCHECKING RESULTS...")

assert result["total_claims"] == 3

assert result["supported_claims"] == 2

assert result["contradicted_claims"] == 0

assert result["uncertain_claims"] == 1

assert result["claims"][0]["verdict"] == "SUPPORTED"

assert result["claims"][1]["verdict"] == "UNCERTAIN"

assert result["claims"][2]["verdict"] == "SUPPORTED"


print("\nClaim 1: SUPPORTED ✅")
print("Claim 2: UNCERTAIN after simulated failure ✅")
print("Claim 3: SUPPORTED ✅")

print("\nAPI resilience test passed successfully!")
