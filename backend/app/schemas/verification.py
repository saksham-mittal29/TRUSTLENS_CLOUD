from pydantic import BaseModel, Field


class VerificationRequest(BaseModel):

    response: str = Field(
        ...,
        min_length=1,
        max_length=20000,
        description="The LLM response that should be verified."
    )