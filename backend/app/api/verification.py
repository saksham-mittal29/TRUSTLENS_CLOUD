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

        # Parse Gemini response
        verdict = "UNCERTAIN"
        confidence = 0
        reason = verification

        for line in verification.splitlines():

            line = line.strip()

            if line.startswith("Verdict:"):
                verdict = line.replace("Verdict:", "").strip()

            elif line.startswith("Confidence:"):
                try:
                    confidence = int(
                        line.replace("Confidence:", "").strip()
                    )
                except ValueError:
                    confidence = 0

            elif line.startswith("Reason:"):
                reason = line.replace("Reason:", "").strip()

        verification_results.append({
            "claim": claim,
            "verdict": verdict,
            "confidence": confidence,
            "reason": reason,
            "evidence": evidence
        })

    # Step 3: Calculate overall Trust Score
    trust_score = calculate_trust_score(verification_results)

    # Step 4: Return complete result
    return {
        "trust_score": trust_score,
        "total_claims": len(verification_results),
        "claims": verification_results
    }