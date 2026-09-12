from pydantic import BaseModel, Field


class VerificationRequest(BaseModel):

    response: str = Field(
        ...,
        min_length=1,
        max_length=20000,
        description="The LLM response that should be verified."
    )


class ClaimResult(BaseModel):
    claim: str
    verdict: str
    confidence: int
    reason: str
    evidence_quality: int
    relevant_sources: list[int]
    source_agreement: int
    historical_reliability: float