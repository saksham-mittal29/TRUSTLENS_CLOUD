from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.verification import router as verification_router
from app.api.history import router as history_router


app = FastAPI(title="TrustLens API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    verification_router,
    prefix="/api"
)

app.include_router(
    history_router,
    prefix="/api"
)


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