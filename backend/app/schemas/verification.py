from pydantic import BaseModel


class VerificationRequest(BaseModel):
    response: str