from app.services.trust_score import (
    calculate_claim_score,
    calculate_trust_score
)


print("=== TRUST SCORE VALIDATION TEST ===")


print("\nTest 1: Normal supported claim")

result = calculate_claim_score({
    "verdict": "SUPPORTED",
    "confidence": 95,
    "evidence_quality": 90
})

print("Score:", result)

assert result == 93.5


print("\nTest 2: String confidence")

result = calculate_claim_score({
    "verdict": "SUPPORTED",
    "confidence": "95",
    "evidence_quality": "90"
})

print("Score:", result)

assert result == 93.5


print("\nTest 3: Scores above 100")

result = calculate_claim_score({
    "verdict": "SUPPORTED",
    "confidence": 150,
    "evidence_quality": 200
})

print("Score:", result)

assert result == 100


print("\nTest 4: Negative scores")

result = calculate_claim_score({
    "verdict": "SUPPORTED",
    "confidence": -50,
    "evidence_quality": -10
})

print("Score:", result)

assert result == 0


print("\nTest 5: Invalid score values")

result = calculate_claim_score({
    "verdict": "SUPPORTED",
    "confidence": "invalid",
    "evidence_quality": None
})

print("Score:", result)

assert result == 0


print("\nTest 6: Invalid verdict")

result = calculate_claim_score({
    "verdict": "UNKNOWN",
    "confidence": 95,
    "evidence_quality": 90
})

print("Score:", result)

assert result == 50


print("\nTest 7: Empty verification")

result = calculate_claim_score({})

print("Score:", result)

assert result == 50


print("\nTest 8: Empty overall verification list")

result = calculate_trust_score([])

print("Overall score:", result)

assert result == 0


print("\nTest 9: Multiple claims")

verifications = [
    {
        "verdict": "SUPPORTED",
        "confidence": 100,
        "evidence_quality": 100
    },
    {
        "verdict": "CONTRADICTED",
        "confidence": 100,
        "evidence_quality": 100
    },
    {
        "verdict": "UNCERTAIN",
        "confidence": 95,
        "evidence_quality": 10
    }
]

result = calculate_trust_score(verifications)

print("Overall score:", result)

assert result == 50


print("\nAll trust score validation tests passed successfully!")