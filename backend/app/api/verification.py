from fastapi import APIRouter, HTTPException
from app.schemas.verification import VerificationRequest
from app.services.claim_extractor import extract_claims

router = APIRouter()


@router.post("/verify")
def verify_response(request: VerificationRequest):
    try:
        claims = extract_claims(request.response)
        return {
            "original_response": request.response,
            "claims": claims
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Claim extraction error: {str(e)}")
