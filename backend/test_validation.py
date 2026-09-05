from app.services.claim_verifier import validate_verification


print("=== TEST CLAIM VERIFICATION VALIDATION ===\n")

# Mock evidence list with 3 sources
mock_evidence = [
    {"title": "Source 1", "url": "https://example.com/1", "snippet": "Snippet 1"},
    {"title": "Source 2", "url": "https://example.com/2", "snippet": "Snippet 2"},
    {"title": "Source 3", "url": "https://example.com/3", "snippet": "Snippet 3"},
]

# Test Case 1: Valid clean data
valid_input = {
    "verdict": "SUPPORTED",
    "confidence": 95,
    "reason": "Strong evidence supporting the claim.",
    "evidence_quality": 90,
    "relevant_sources": [1, 2]
}

result_1 = validate_verification(valid_input, mock_evidence)
print("Test 1 (Valid Input):")
print(result_1)
assert result_1["verdict"] == "SUPPORTED"
assert result_1["confidence"] == 95
assert result_1["evidence_quality"] == 90
assert result_1["relevant_sources"] == [1, 2]

# Test Case 2: Out of bounds confidence & evidence quality, invalid verdict
edge_input = {
    "verdict": "INVALID_VERDICT",
    "confidence": 150,
    "reason": 12345,  # Non-string reason
    "evidence_quality": -20,
    "relevant_sources": ["1", 2, 2, 99, "invalid"]  # String int, duplicate, out-of-bounds, non-int
}

result_2 = validate_verification(edge_input, mock_evidence)
print("\nTest 2 (Edge cases - invalid verdict, clamped scores, filtered sources):")
print(result_2)
assert result_2["verdict"] == "UNCERTAIN"
assert result_2["confidence"] == 100
assert result_2["evidence_quality"] == 0
assert isinstance(result_2["reason"], str)
assert result_2["relevant_sources"] == [1, 2]

# Test Case 3: Empty / malformed dictionary
result_3 = validate_verification({}, mock_evidence)
print("\nTest 3 (Empty input):")
print(result_3)
assert result_3["verdict"] == "UNCERTAIN"
assert result_3["confidence"] == 0
assert result_3["evidence_quality"] == 0
assert result_3["relevant_sources"] == []

print("\nAll validation tests passed successfully!")
