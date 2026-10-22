# TrustLens

> **Automated Claim Verification & Evidence-Backed Trust Scoring Engine**

TrustLens is an enterprise-grade AI fact-checking and automated claim verification platform. It ingests arbitrary unstructured text, decomposes it into atomic factual claims, searches live web evidence, evaluates claims using Natural Language Inference (NLI), tracks domain source reliability, and computes an explainable, multi-factor **Trust Score (0–100)**.

---

## Visual Showcase

### 1. Analytics Dashboard
Overview of processed verifications, system-wide mean accuracy metrics, claim distribution (Supported, Contradicted, Uncertain), and recent verification cards with real-time trust ratings.

![TrustLens Dashboard](docs/screenshots/dashboard.png)

---

### 2. Claim Verification Console
Interactive workspace for submitting unstructured statements, news articles, or model outputs for real-time claim extraction and multi-source evidence verification.

![TrustLens Verify](docs/screenshots/verify.png)

---

### 3. Verification History & Audit Trail
Historical log of all previous verification queries with detailed trust score breakdowns, claim counts, and drill-down inspections.

![TrustLens History](docs/screenshots/history.png)

---

## Key Features

- **Automated Claim Extraction**: Parses unstructured input text and decomposes it into independent, testable factual propositions using Google Gemini.
- **Real-Time Evidence Gathering**: Automated web search and snippet scraping across diverse public sources to retrieve grounding evidence.
- **Natural Language Inference (NLI) Verification**: Evaluates each extracted claim against collected evidence premises to assign verdicts:
  - `SUPPORTED`: Claim is confirmed by credible evidence.
  - `CONTRADICTED`: Claim is refuted by evidence.
  - `UNCERTAIN`: Insufficient evidence or conflicting reports.
- **Dynamic Source Reliability**: Tracks historical reliability per domain in PostgreSQL to weight evidence credibility.
- **Composite Trust Scoring**: Multi-factor Bayesian-inspired formula weighting claim verdicts, evidence quality, source agreement, and domain authority to output a calibrated 0–100 score.
- **NLI Benchmarking Suite**: Includes an evaluation framework comparing Gemini-based inference with fine-tuned BERT NLI models on the FEVER dataset.
- **Secure Authentication**: Firebase Auth with JWT verification on protected FastAPI endpoints.

---

## Architecture & Technology Stack

```mermaid
graph TD
    A[Client / Frontend Vite + React] -->|JWT Bearer Token| B[FastAPI Gateway]
    B --> C[Firebase Admin SDK Auth]
    B --> D[Claim Extractor LLM]
    D --> E[Evidence Search & Scraper]
    E --> F[NLI Claim Verifier]
    F --> G[Source Reliability & Trust Scorer]
    G --> H[(PostgreSQL Database)]
    H -->|Alembic Migrations| H
```

### Frontend
- **Framework**: React 19 + TypeScript + Vite
- **Styling**: Tailwind CSS v4 + Lucide React Icons
- **Auth**: Firebase Client SDK
- **Routing**: React Router v7

### Backend
- **Web API**: FastAPI + Uvicorn
- **Database & ORM**: PostgreSQL + SQLAlchemy 2.0 + Alembic migrations
- **LLM / Inference**: Google Gemini API (`google-genai`)
- **Evaluation & Benchmarks**: Hugging Face Transformers (`bert-base-uncased-MNLI`), PyTorch, Scikit-learn
- **Search**: DuckDuckGo Search (`duckduckgo_search`)

---

## Getting Started

### Prerequisites
- **Python**: 3.11+
- **Node.js**: 18+ (npm 9+)
- **PostgreSQL**: 14+ running locally or remotely

---

### 1. Environment Configuration

#### Backend Configuration
Create `backend/.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/trustlens
FIREBASE_CREDENTIALS_PATH=./trustlens_firebase_admin_sdk.json
```

#### Frontend Configuration
Create `frontend/.env`:
```env
VITE_FIREBASE_API_KEY=your_firebase_api_key
VITE_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your_project_id
VITE_FIREBASE_STORAGE_BUCKET=your_project.firebasestorage.app
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
VITE_FIREBASE_APP_ID=your_app_id
```

---

### 2. Backend Setup & Run

1. Navigate to the backend directory and set up the virtual environment:
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Run database migrations:
   ```bash
   alembic upgrade head
   ```

3. Start the FastAPI development server:
   ```bash
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```

The backend will be available at:
- **API URL**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

### 3. Frontend Setup & Run

1. Navigate to the frontend directory and install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Start the Vite development server:
   ```bash
   npm run dev
   ```

3. Open your browser and navigate to:
   - **Frontend App**: [http://localhost:5173](http://localhost:5173)

---

## API Endpoints Reference

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | API root status | No |
| `GET` | `/health` | Service health status | No |
| `POST` | `/api/verify` | Submit statement, extract claims & verify against evidence | Yes (Bearer Token) |
| `GET` | `/api/verifications` | Fetch user's historical verifications list | Yes (Bearer Token) |
| `GET` | `/api/verifications/{id}` | Fetch deep-dive verification report with claims & evidence | Yes (Bearer Token) |

---

## Automated Testing Suite

The project includes unit, API contract, resilience, and database integration tests using `pytest`:

```bash
cd backend
source venv/bin/activate

# Run all unit tests
pytest tests/unit/

# Run API contract & resilience tests
pytest tests/api/

# Run database integration tests
pytest tests/database/

# Run the complete test suite
pytest
```

---

## Model Evaluation & Benchmarking

TrustLens provides a benchmarking harness comparing LLM verification against fine-tuned BERT NLI on the FEVER dataset:

```bash
cd backend
source venv/bin/activate

# Run evaluation on cached dataset
python evaluation/evaluate_bert_nli.py

# Run live claim evaluation
python evaluation/run_evaluation.py
```

Evaluation metrics produced:
- **Accuracy & Macro-F1** across 3 classes (`SUPPORTED`, `CONTRADICTED`, `NOT ENOUGH EVIDENCE`)
- **Per-Class Precision, Recall, and Support**
- **Brier Score & Expected Calibration Error (ECE)** for confidence reliability
- **Confusion Matrix**

---

## Project Structure

```text
trustlens/
├── backend/
│   ├── alembic/                      # Database migration scripts
│   ├── app/
│   │   ├── api/                      # Route controllers (verify, history, auth)
│   │   ├── database/                 # PostgreSQL connection & session factory
│   │   ├── models/                   # SQLAlchemy models (User, Verification, Claim, Evidence)
│   │   ├── schemas/                  # Pydantic request & response models
│   │   └── services/                 # Verification engine, claim extractor, trust scoring
│   ├── evaluation/                   # FEVER dataset, BERT NLI evaluation & benchmarks
│   ├── tests/                        # Comprehensive unit, API, and DB tests
│   ├── requirements.txt              # Backend dependencies
│   └── main.py                       # FastAPI application entrypoint
├── docs/
│   └── screenshots/                  # Application UI screenshots
│       ├── dashboard.png
│       ├── history.png
│       └── verify.png
└── frontend/
    ├── public/                       # Static public assets
    ├── src/
    │   ├── components/               # UI components (Header, Sidebar, VerificationCard)
    │   ├── pages/                    # Views (Dashboard, Verify, History, Login)
    │   ├── firebase.ts               # Firebase Auth initialization
    │   └── App.tsx                   # Routing & application shell
    ├── package.json                  # Frontend dependencies & scripts
    └── vite.config.ts                # Vite build configuration
```

---

## License

This project is licensed under the MIT License.