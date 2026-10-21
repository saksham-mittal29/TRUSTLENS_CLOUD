import pytest
from app.services.trust_score import (
    calculate_claim_score,
    calculate_trust_score,
    calculate_domain_risk,
    _safe_score,
)


# ==============================================================================
# 1. Component & Type Conversion Tests (_safe_score)
# ==============================================================================

def test_safe_score_valid_numbers():
    assert _safe_score(0) == 0.0
    assert _safe_score(50) == 50.0
    assert _safe_score(100) == 100.0
    assert _safe_score(87.5) == 87.5


def test_safe_score_string_parsing():
    assert _safe_score("95") == 95.0
    assert _safe_score("0") == 0.0
    assert _safe_score("72.4") == 72.4


def test_safe_score_clamping_boundaries():
    assert _safe_score(150) == 100.0
    assert _safe_score(99999) == 100.0
    assert _safe_score(-20) == 0.0
    assert _safe_score(-0.01) == 0.0


def test_safe_score_invalid_inputs_fallback_to_zero():
    assert _safe_score("invalid") == 0.0
    assert _safe_score("") == 0.0
    assert _safe_score(None) == 0.0
    assert _safe_score([]) == 0.0
    assert _safe_score({}) == 0.0


# ==============================================================================
# 2. Domain Risk Assessment Tests (calculate_domain_risk)
# ==============================================================================

def test_domain_risk_high_risk_keywords():
    # Medical / Health
    assert calculate_domain_risk("This medical drug cures cancer.") == 90.0
    assert calculate_domain_risk("Patient diagnosis requires immediate treatment.") == 90.0
    assert calculate_domain_risk("Aspirin is a common medication.") == 90.0
    # Financial
    assert calculate_domain_risk("The stock market investment yielded high returns.") == 90.0
    assert calculate_domain_risk("The bank charges tax on international wire transfers.") == 90.0
    assert calculate_domain_risk("Insurance policy covers flood damage.") == 90.0
    # Legal
    assert calculate_domain_risk("The supreme court ruled on the contract lawsuit.") == 90.0
    assert calculate_domain_risk("Under criminal law, this is illegal.") == 90.0


def test_domain_risk_medium_risk_keywords():
    # Tech / Cloud / Security
    assert calculate_domain_risk("The PostgreSQL database stores user records.") == 60.0
    assert calculate_domain_risk("AWS cloud infrastructure handles the backend.") == 60.0
    assert calculate_domain_risk("Cybersecurity protocols protect user privacy.") == 60.0
    assert calculate_domain_risk("Python programming language is versatile.") == 60.0
    assert calculate_domain_risk("New software technology improves productivity.") == 60.0


def test_domain_risk_low_risk_default():
    assert calculate_domain_risk("The Eiffel Tower is located in Paris.") == 30.0
    assert calculate_domain_risk("Mount Everest is the highest mountain on Earth.") == 30.0
    assert calculate_domain_risk("Water boils at 100 degrees Celsius.") == 30.0
    assert calculate_domain_risk("") == 30.0


def test_domain_risk_case_insensitivity():
    assert calculate_domain_risk("MEDICAL RESEARCH STUDY") == 90.0
    assert calculate_domain_risk("CLOUD Database System") == 60.0


# ==============================================================================
# 3. Single Claim Trust Score Calculation (calculate_claim_score)
# Formula: 0.45C + 0.25E + 0.15A + 0.15R - RiskPenalty
# where R = 0.70 * source_reliability + 0.30 * historical_reliability
# and RiskPenalty = domain_risk * 0.10
# ==============================================================================

def test_supported_claim_perfect_scores_low_risk():
    # C=100, E=100, A=100, SR=100, HR=100 -> R = 100
    # base = 100*0.45 + 100*0.25 + 100*0.15 + 100*0.15 = 100.0
    # low risk claim = 30 -> penalty = 3.0
    # score = 100 - 3.0 = 97.0
    verification = {
        "claim": "The Eiffel Tower is in Paris.",
        "verdict": "SUPPORTED",
        "confidence": 100,
        "evidence_quality": 100,
        "source_agreement": 100,
        "source_reliability": 100,
        "historical_reliability": 100,
    }
    assert calculate_claim_score(verification) == 97.0


def test_supported_claim_perfect_scores_medium_risk():
    # base = 100.0, medium risk = 60 -> penalty = 6.0 -> score = 94.0
    verification = {
        "claim": "The cloud database provides automated backups.",
        "verdict": "SUPPORTED",
        "confidence": 100,
        "evidence_quality": 100,
        "source_agreement": 100,
        "source_reliability": 100,
        "historical_reliability": 100,
    }
    assert calculate_claim_score(verification) == 94.0


def test_supported_claim_perfect_scores_high_risk():
    # base = 100.0, high risk = 90 -> penalty = 9.0 -> score = 91.0
    verification = {
        "claim": "The medical drug was approved by regulatory health authorities.",
        "verdict": "SUPPORTED",
        "confidence": 100,
        "evidence_quality": 100,
        "source_agreement": 100,
        "source_reliability": 100,
        "historical_reliability": 100,
    }
    assert calculate_claim_score(verification) == 91.0


def test_supported_claim_partial_metrics():
    # C=80 (36), E=70 (17.5), A=60 (9.0), SR=90, HR=50 -> R = 63 + 15 = 78 (11.7)
    # base = 36 + 17.5 + 9.0 + 11.7 = 74.2
    # low risk claim = 30 -> penalty = 3.0
    # score = 74.2 - 3.0 = 71.2
    verification = {
        "claim": "Paris has many bridges.",
        "verdict": "SUPPORTED",
        "confidence": 80,
        "evidence_quality": 70,
        "source_agreement": 60,
        "source_reliability": 90,
        "historical_reliability": 50,
    }
    assert calculate_claim_score(verification) == 71.2


def test_contradicted_claim_high_confidence():
    # When a falsehood is strongly contradicted by strong evidence:
    # C=100 (0), E=100 (0), A=100 (0), R=100 (0) -> base = 0.0
    # penalty = 3.0 -> clamped to 0.0
    verification = {
        "claim": "The Eiffel Tower was built in 2020.",
        "verdict": "CONTRADICTED",
        "confidence": 100,
        "evidence_quality": 100,
        "source_agreement": 100,
        "source_reliability": 100,
        "historical_reliability": 100,
    }
    assert calculate_claim_score(verification) == 0.0


def test_contradicted_claim_weak_evidence():
    # If contradiction confidence was only 20% and evidence quality was 20%:
    # (100-20)*0.45=36, (100-20)*0.25=20, (100-20)*0.15=12, (100-20)*0.15=12
    # base = 36 + 20 + 12 + 12 = 80.0
    # penalty = 3.0 -> score = 77.0
    verification = {
        "claim": "The Eiffel Tower is painted green.",
        "verdict": "CONTRADICTED",
        "confidence": 20,
        "evidence_quality": 20,
        "source_agreement": 20,
        "source_reliability": 20,
        "historical_reliability": 20,
    }
    assert calculate_claim_score(verification) == 77.0


def test_uncertain_claim_always_returns_neutral_50():
    # UNCERTAIN claims should always receive neutral score of 50.0 regardless of metrics
    verification = {
        "claim": "This medical drug may cure headaches.",
        "verdict": "UNCERTAIN",
        "confidence": 95,
        "evidence_quality": 90,
        "source_agreement": 90,
        "source_reliability": 90,
    }
    assert calculate_claim_score(verification) == 50.0


def test_zero_evidence_defaults_and_missing_keys():
    # When zero evidence exists and verifier returns UNCERTAIN
    verification = {
        "verdict": "UNCERTAIN",
        "confidence": 0,
        "evidence_quality": 0,
        "relevant_sources": []
    }
    assert calculate_claim_score(verification) == 50.0


def test_invalid_payload_and_unknown_verdict():
    assert calculate_claim_score({}) == 50.0
    assert calculate_claim_score(None) == 50.0
    assert calculate_claim_score({"verdict": "UNKNOWN_VERDICT"}) == 50.0
    assert calculate_claim_score({"verdict": "NOT_ENOUGH_EVIDENCE"}) == 50.0


# ==============================================================================
# 4. Overall Multi-Claim Trust Score Aggregation (calculate_trust_score)
# ==============================================================================

def test_overall_trust_score_empty_claims_list():
    assert calculate_trust_score([]) == 0.0
    assert calculate_trust_score(None) == 0.0


def test_overall_trust_score_single_claim():
    verifications = [
        {
            "claim": "The Eiffel Tower is in Paris.",
            "verdict": "SUPPORTED",
            "confidence": 100,
            "evidence_quality": 100,
            "source_agreement": 100,
            "source_reliability": 100,
            "historical_reliability": 100,
        }
    ]
    assert calculate_trust_score(verifications) == 97.0


def test_overall_trust_score_multiple_mixed_claims():
    verifications = [
        # Claim 1: SUPPORTED low risk (score = 97.0)
        {
            "claim": "The Eiffel Tower is in Paris.",
            "verdict": "SUPPORTED",
            "confidence": 100,
            "evidence_quality": 100,
            "source_agreement": 100,
            "source_reliability": 100,
            "historical_reliability": 100,
        },
        # Claim 2: CONTRADICTED high confidence low risk (score = 0.0)
        {
            "claim": "The Eiffel Tower was built in 2020.",
            "verdict": "CONTRADICTED",
            "confidence": 100,
            "evidence_quality": 100,
            "source_agreement": 100,
            "source_reliability": 100,
            "historical_reliability": 100,
        },
        # Claim 3: UNCERTAIN (score = 50.0)
        {
            "claim": "The Eiffel Tower will stand for 1000 years.",
            "verdict": "UNCERTAIN",
            "confidence": 0,
            "evidence_quality": 0,
        }
    ]
    # Average = (97.0 + 0.0 + 50.0) / 3 = 147.0 / 3 = 49.0
    assert calculate_trust_score(verifications) == 49.0


def test_overall_trust_score_all_supported_high_risk():
    verifications = [
        {
            "claim": "Aspirin is a medical drug.",
            "verdict": "SUPPORTED",
            "confidence": 100,
            "evidence_quality": 100,
            "source_agreement": 100,
            "source_reliability": 100,
            "historical_reliability": 100,
        },
        {
            "claim": "Penicillin is a medical treatment.",
            "verdict": "SUPPORTED",
            "confidence": 100,
            "evidence_quality": 100,
            "source_agreement": 100,
            "source_reliability": 100,
            "historical_reliability": 100,
        }
    ]
    # Both claims are high risk (penalty = 9.0 -> score = 91.0 each)
    assert calculate_trust_score(verifications) == 91.0
