from fastapi import FastAPI
from app.api.verification import router as verification_router

app = FastAPI(title="TrustLens API")

app.include_router(verification_router, prefix="/api")


@app.get("/")
def root():
    return {
        "message": "TrustLens API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }

