from app.services.trust_score import calculate_claim_score, calculate_trust_score


print("=== TRUST SCORE TEST ===")


supported_claim = {
    "verdict": "SUPPORTED",
    "confidence": 98,
    "evidence_quality": 95,
    "relevant_sources": [1, 2, 3]
}

contradicted_claim = {
    "verdict": "CONTRADICTED",
    "confidence": 98,
    "evidence_quality": 95,
    "relevant_sources": [1, 2, 3]
}

uncertain_claim = {
    "verdict": "UNCERTAIN",
    "confidence": 50,
    "evidence_quality": 50,
    "relevant_sources": []
}


supported_score = calculate_claim_score(supported_claim)
contradicted_score = calculate_claim_score(contradicted_claim)
uncertain_score = calculate_claim_score(uncertain_claim)


print(f"Supported Claim Score: {supported_score}")
print(f"Contradicted Claim Score: {contradicted_score}")
print(f"Uncertain Claim Score: {uncertain_score}")


all_claims = [
    supported_claim,
    contradicted_claim,
    uncertain_claim
]

overall_score = calculate_trust_score(all_claims)

print(f"Overall Trust Score: {overall_score}")