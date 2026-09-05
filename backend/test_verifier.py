from app.services.evidence_search import search_evidence
from app.services.claim_verifier import verify_claim


claim = "The Eiffel Tower is 500 meters tall."


print("\nSearching for evidence...\n")

evidence = search_evidence(claim)

print("Evidence found:")
for item in evidence:
    print(f"- {item.get('title')}")
    print(f"  {item.get('url')}")


print("\nVerifying claim...\n")

result = verify_claim(claim, evidence)


print("\n===================================")
print("VERIFICATION RESULT")
print("===================================")

print(f"Verdict: {result['verdict']}")
print(f"Confidence: {result['confidence']}")
print(f"Reason: {result['reason']}")
print(f"Evidence Quality: {result.get('evidence_quality')}")
print(f"Relevant Sources: {result.get('relevant_sources')}")