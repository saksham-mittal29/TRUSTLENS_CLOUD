from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.verification import VerificationRequest
from app.api.dependencies import get_current_firebase_user
from app.services.claim_extractor import extract_claims
from app.services.evidence_search import search_evidence
from app.services.claim_verifier import verify_claim
from app.services.trust_score import calculate_trust_score
from app.services.verification_repository import save_verification
from app.services.user_repository import get_or_create_user
from app.services.source_reliability_repository import (
    get_domain,
    get_historical_reliability,
    update_source_reliability,
)


router = APIRouter()


@router.post("/verify")
def verify_response(
    request: VerificationRequest,
    db: Session = Depends(get_db),
    firebase_user: dict = Depends(get_current_firebase_user)
):

    firebase_uid = firebase_user["uid"]

    user = get_or_create_user(
        db=db,
        firebase_uid=firebase_uid
    )

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
        except Exception:
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

        relevant_sources = verification.get("relevant_sources", [])

        historical_reliabilities = []

        for source_number in relevant_sources:
            if 1 <= source_number <= len(evidence):
                source = evidence[source_number - 1]
                domain = get_domain(source.get("url", ""))

                if domain:
                    historical_reliabilities.append(
                        get_historical_reliability(
                            db=db,
                            domain=domain,
                        )
                    )

        if historical_reliabilities:
            verification["historical_reliability"] = round(
                sum(historical_reliabilities)
                / len(historical_reliabilities),
                2,
            )
        else:
            verification["historical_reliability"] = 50.0



        # Build complete claim result
        verification_results.append({
            "claim": claim,
            "verdict": verification.get("verdict", "UNCERTAIN"),
            "confidence": verification.get("confidence", 0),
            "reason": verification.get("reason", ""),
            "evidence_quality": verification.get("evidence_quality", 0),
            "source_agreement": verification.get("source_agreement", 0),
            "source_reliability": verification.get("source_reliability", 0),
            "historical_reliability": verification.get("historical_reliability", 50.0),
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

    # Step 4: Save verification to PostgreSQL
    try:
        saved_verification = save_verification(
            db=db,
            original_response=request.response,
            trust_score=trust_score,
            results=verification_results,
            user_id=user.id
        )

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to save verification: {str(exc)}"
        )

    # Step 5: Update historical source reliability
    for result in verification_results:
        claim_evidence = result.get("evidence", [])
        for source_number in result.get("relevant_sources", []):
            if 1 <= source_number <= len(claim_evidence):
                source = claim_evidence[source_number - 1]
                domain = get_domain(source.get("url", ""))

                if domain:
                    update_source_reliability(
                        db=db,
                        domain=domain,
                        verdict=result.get("verdict", "UNCERTAIN"),
                    )

    # Step 6: Return complete result
    return {
        "verification_id": saved_verification.id,
        "trust_score": trust_score,
        "total_claims": len(verification_results),
        "supported_claims": supported_claims,
        "contradicted_claims": contradicted_claims,
        "uncertain_claims": uncertain_claims,
        "claims": verification_results
    }