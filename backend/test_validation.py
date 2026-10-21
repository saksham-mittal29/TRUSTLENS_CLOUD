from app.services.claim_verifier import validate_verification


evidence = [
    {
        "title": "Source 1",
        "url": "https://example.com/1",
        "snippet": "Example evidence"
    },
    {
        "title": "Source 2",
        "url": "https://example.com/2",
        "snippet": "More evidence"
    }
]


print("=== TEST 1: VALID DATA ===")

valid_data = {
    "verdict": "SUPPORTED",
    "confidence": 95,
    "reason": "The evidence directly supports the claim.",
    "evidence_quality": 90,
    "relevant_sources": [1, 2]
}

print(validate_verification(valid_data, evidence))


print("\n=== TEST 2: INVALID VERDICT ===")

invalid_verdict = {
    "verdict": "TRUE",
    "confidence": 95,
    "reason": "Test",
    "evidence_quality": 90,
    "relevant_sources": [1]
}

print(validate_verification(invalid_verdict, evidence))


print("\n=== TEST 3: INVALID SCORES ===")

invalid_scores = {
    "verdict": "SUPPORTED",
    "confidence": 150,
    "reason": "Test",
    "evidence_quality": -20,
    "relevant_sources": [1]
}

print(validate_verification(invalid_scores, evidence))


print("\n=== TEST 4: INVALID SOURCES ===")

invalid_sources = {
    "verdict": "SUPPORTED",
    "confidence": "95",
    "reason": "Test",
    "evidence_quality": "90",
    "relevant_sources": [1, 2, 99, "hello", 2]
}

print(validate_verification(invalid_sources, evidence))


print("\n=== TEST 5: COMPLETELY INVALID DATA ===")

completely_invalid = {
    "verdict": "WHATEVER",
    "confidence": "abc",
    "reason": None,
    "evidence_quality": "bad",
    "relevant_sources": "not a list"
}

print(validate_verification(completely_invalid, evidence))