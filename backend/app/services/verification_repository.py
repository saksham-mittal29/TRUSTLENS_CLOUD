from sqlalchemy.orm import Session

from app.models import Verification, Claim, Evidence


def save_verification(
    db: Session,
    original_response: str,
    trust_score: float,
    results: list,
    user_id: int | None = None
):
    supported_claims = sum(
        1 for result in results
        if result.get("verdict") == "SUPPORTED"
    )

    contradicted_claims = sum(
        1 for result in results
        if result.get("verdict") == "CONTRADICTED"
    )

    uncertain_claims = sum(
        1 for result in results
        if result.get("verdict") == "UNCERTAIN"
    )

    verification = Verification(
        user_id=user_id,
        original_response=original_response,
        trust_score=trust_score,
        total_claims=len(results),
        supported_claims=supported_claims,
        contradicted_claims=contradicted_claims,
        uncertain_claims=uncertain_claims
    )

    db.add(verification)
    db.flush()

    for result in results:
        claim = Claim(
            verification_id=verification.id,
            claim_text=result.get("claim", ""),
            verdict=result.get("verdict", "UNCERTAIN"),
            confidence=result.get("confidence", 0),
            reason=result.get("reason", ""),
            evidence_quality=result.get("evidence_quality", 0)
        )

        db.add(claim)
        db.flush()

        evidence_items = result.get("evidence", [])

        for evidence_data in evidence_items:
            evidence = Evidence(
                claim_id=claim.id,
                title=evidence_data.get("title", ""),
                url=evidence_data.get("url", ""),
                snippet=evidence_data.get("snippet", "")
            )

            db.add(evidence)

    db.commit()
    db.refresh(verification)

    return verification
