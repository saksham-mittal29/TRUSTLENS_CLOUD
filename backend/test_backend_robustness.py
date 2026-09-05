from unittest.mock import patch

from app.api.verification import verify_response
from app.schemas.verification import VerificationRequest


print("=== TRUSTLENS BACKEND ROBUSTNESS TEST ===")


# Simulated claims
fake_claims = [
    {"claim": "Claim one is supported."},
    {"claim": "Claim two is contradicted."},
    {"claim": "Claim three is uncertain."},
    {"claim": "Claim four fails verification."}
]


def fake_search_evidence(claim):

    # Claim three has no evidence
    if "Claim three" in claim:
        return []

    return [
        {
            "title": "Test Source",
            "url": "https://example.com",
            "snippet": "Test evidence"
        }
    ]


def fake_verify_claim(claim, evidence):

    # Claim four simulates a verification failure
    if "Claim four" in claim:
        raise Exception("Simulated Gemini verification failure")

    # Claim two is contradicted
    if "Claim two" in claim:
        return {
            "verdict": "CONTRADICTED",
            "confidence": 95,
            "reason": "Evidence contradicts the claim.",
            "evidence_quality": 90,
            "relevant_sources": [1]
        }

    # Claim three should never reach Gemini because evidence is empty
    if "Claim three" in claim:
        raise Exception("This should not be called")

    # Claim one is supported
    return {
        "verdict": "SUPPORTED",
        "confidence": 95,
        "reason": "Evidence supports the claim.",
        "evidence_quality": 90,
        "relevant_sources": [1]
    }


request = VerificationRequest(
    response="Test response containing four different claims."
)


with patch(
    "app.api.verification.extract_claims",
    return_value=fake_claims
), patch(
    "app.api.verification.search_evidence",
    side_effect=fake_search_evidence
), patch(
    "app.api.verification.verify_claim",
    side_effect=fake_verify_claim
):

    result = verify_response(request)


print("\nFINAL RESULT:")
print(result)


print("\nCHECKING RESULTS...")


# Basic response checks
assert result["total_claims"] == 4

assert result["supported_claims"] == 1

assert result["contradicted_claims"] == 1

assert result["uncertain_claims"] == 2


# Claim 1
assert result["claims"][0]["verdict"] == "SUPPORTED"


# Claim 2
assert result["claims"][1]["verdict"] == "CONTRADICTED"


# Claim 3
assert result["claims"][2]["verdict"] == "UNCERTAIN"
assert result["claims"][2]["confidence"] == 0
assert result["claims"][2]["evidence_quality"] == 0
assert result["claims"][2]["relevant_sources"] == []


# Claim 4
assert result["claims"][3]["verdict"] == "UNCERTAIN"
assert result["claims"][3]["confidence"] == 0
assert result["claims"][3]["evidence_quality"] == 0


# Trust score must remain valid
assert 0 <= result["trust_score"] <= 100


print("\nClaim 1: SUPPORTED ✅")
print("Claim 2: CONTRADICTED ✅")
print("Claim 3: No evidence → UNCERTAIN ✅")
print("Claim 4: Verification failure → UNCERTAIN ✅")
print("Trust score remains within 0–100 ✅")

print("\nAll backend robustness tests passed successfully! 🎉")
