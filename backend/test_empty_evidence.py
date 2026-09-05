from app.services.claim_verifier import verify_claim


print("=== EMPTY EVIDENCE TEST ===")

claim = "The Eiffel Tower is located on Mars."

result = verify_claim(claim, [])

print("Result:")
print(result)

assert result["verdict"] == "UNCERTAIN"
assert result["confidence"] == 0
assert result["evidence_quality"] == 0
assert result["relevant_sources"] == []

print("\nEmpty evidence test passed successfully!")
