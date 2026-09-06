from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Verification
from app.api.dependencies import get_current_firebase_user
from app.services.user_repository import get_or_create_user


router = APIRouter()


@router.get("/verifications")
def get_verification_history(
    db: Session = Depends(get_db),
    firebase_user: dict = Depends(get_current_firebase_user)
):
    firebase_uid = firebase_user["uid"]

    user = get_or_create_user(
        db=db,
        firebase_uid=firebase_uid
    )

    verifications = (
        db.query(Verification)
        .filter(Verification.user_id == user.id)
        .order_by(Verification.created_at.desc())
        .all()
    )

    return {
        "total": len(verifications),
        "verifications": [
            {
                "id": verification.id,
                "trust_score": verification.trust_score,
                "total_claims": verification.total_claims,
                "supported_claims": verification.supported_claims,
                "contradicted_claims": verification.contradicted_claims,
                "uncertain_claims": verification.uncertain_claims,
                "created_at": verification.created_at,
            }
            for verification in verifications
        ]
    }


@router.get("/verifications/{verification_id}")
def get_verification_detail(
    verification_id: int,
    db: Session = Depends(get_db),
    firebase_user: dict = Depends(get_current_firebase_user)
):
    firebase_uid = firebase_user["uid"]

    user = get_or_create_user(
        db=db,
        firebase_uid=firebase_uid
    )

    verification = (
        db.query(Verification)
        .filter(
            Verification.id == verification_id,
            Verification.user_id == user.id
        )
        .first()
    )

    if not verification:
        raise HTTPException(
            status_code=404,
            detail="Verification not found"
        )

    return {
        "id": verification.id,
        "original_response": verification.original_response,
        "trust_score": verification.trust_score,
        "total_claims": verification.total_claims,
        "supported_claims": verification.supported_claims,
        "contradicted_claims": verification.contradicted_claims,
        "uncertain_claims": verification.uncertain_claims,
        "created_at": verification.created_at,
        "claims": [
            {
                "id": claim.id,
                "claim": claim.claim_text,
                "verdict": claim.verdict,
                "confidence": claim.confidence,
                "reason": claim.reason,
                "evidence_quality": claim.evidence_quality,
                "created_at": claim.created_at,
                "evidence": [
                    {
                        "id": evidence.id,
                        "title": evidence.title,
                        "url": evidence.url,
                        "snippet": evidence.snippet,
                        "created_at": evidence.created_at,
                    }
                    for evidence in claim.evidence
                ],
            }
            for claim in verification.claims
        ]
    }