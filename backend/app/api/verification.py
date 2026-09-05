from fastapi import APIRouter, HTTPException

from app.schemas.verification import VerificationRequest
from app.services.claim_extractor import extract_claims
from app.services.evidence_search import search_evidence
from app.services.claim_verifier import verify_claim
from app.services.trust_score import calculate_trust_score


router = APIRouter()


@router.post("/verify")
def verify_response(request: VerificationRequest):

    # Step 1: Extract claims
    try:
        claims = extract_claims(request.response)

    except Exception as exc:
        error_message = str(exc)

        if "429" in error_message or "RESOURCE_EXHAUSTED" in error_message:
            raise HTTPException(
                status_code=429,
                detail="Gemini API quota exceeded. Please try again later."
            )

        if "503" in error_message or "UNAVAILABLE" in error_message:
            raise HTTPException(
                status_code=503,
                detail="Gemini AI service is temporarily unavailable. Please try again later."
            )

        raise HTTPException(
            status_code=500,
            detail=f"Claim extraction failed: {error_message}"
        )

    verification_results = []

    # Step 2: Process every claim
    for item in claims:

        claim = item["claim"]

        # Search for evidence
        try:
            evidence = search_evidence(claim)
        except Exception as exc:
            evidence = []

        # Verify claim against evidence
        try:
            verification = verify_claim(claim, evidence)
        except Exception as exc:
            verification = {
                "verdict": "UNCERTAIN",
                "confidence": 0,
                "reason": f"Verification temporarily failed: {str(exc)}",
                "evidence_quality": 0,
                "relevant_sources": []
            }

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