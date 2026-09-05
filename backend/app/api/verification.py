from fastapi import APIRouter

from app.schemas.verification import VerificationRequest
from app.services.claim_extractor import extract_claims
from app.services.evidence_search import search_evidence
from app.services.claim_verifier import verify_claim
from app.services.trust_score import calculate_trust_score


router = APIRouter()


@router.post("/verify")
def verify_response(request: VerificationRequest):

    # Step 1: Extract claims
    claims = extract_claims(request.response)

    verification_results = []

    # Step 2: Process every claim
    for item in claims:

        claim = item["claim"]

        # Search for evidence
        evidence = search_evidence(claim)

        # Verify claim against evidence
        verification = verify_claim(claim, evidence)

        # Build complete claim result
        verification_results.append({
            "claim": claim,
            "verdict": verification.get("verdict", "UNCERTAIN"),
            "confidence": verification.get("confidence", 0),
            "reason": verification.get("reason", ""),
            "evidence_quality": verification.get("evidence_quality", 0),
            "relevant_sources": verification.get("relevant_sources", []),
            "evidence": evidence
        })

    # Step 3: Calculate overall Trust Score
    trust_score = calculate_trust_score(verification_results)

    supported_claims = sum(
        1 for result in verification_results
        if result["verdict"] == "SUPPORTED"
    )

    contradicted_claims = sum(
        1 for result in verification_results
        if result["verdict"] == "CONTRADICTED"
    )

    uncertain_claims = sum(
        1 for result in verification_results
        if result["verdict"] == "UNCERTAIN"
    )

    # Step 4: Return complete result
    return {
        "trust_score": trust_score,
        "total_claims": len(verification_results),
        "supported_claims": supported_claims,
        "contradicted_claims": contradicted_claims,
        "uncertain_claims": uncertain_claims,
        "claims": verification_results
    }