def _safe_score(value) -> float:
    """
    Convert a score to a safe number between 0 and 100.
    """

    try:
        value = float(value)
    except (ValueError, TypeError):
        value = 0

    return max(0, min(100, value))


def calculate_domain_risk(claim: str) -> float:
    """
    Estimate the risk level of a claim based on its domain.
    Returns a value from 0 to 100.
    """

    claim_lower = claim.lower()

    high_risk_keywords = [
        "medical",
        "medicine",
        "health",
        "disease",
        "diagnosis",
        "symptom",
        "treatment",
        "drug",
        "medication",
        "legal",
        "law",
        "lawsuit",
        "court",
        "contract",
        "financial",
        "finance",
        "investment",
        "investing",
        "stock",
        "tax",
        "bank",
        "insurance",
    ]

    medium_risk_keywords = [
        "security",
        "cybersecurity",
        "privacy",
        "programming",
        "software",
        "database",
        "cloud",
        "technology",
    ]

    if any(keyword in claim_lower for keyword in high_risk_keywords):
        return 90

    if any(keyword in claim_lower for keyword in medium_risk_keywords):
        return 60

    return 30


def calculate_claim_score(verification: dict) -> float:
    """
    Calculate a trust score for a single verified claim.

    The score considers:
    - verdict
    - confidence
    - evidence quality
    """

    if not isinstance(verification, dict):
        verification = {}

    verdict = verification.get("verdict", "UNCERTAIN")
    confidence = _safe_score(
        verification.get("confidence", 0)
    )
    evidence_quality = _safe_score(
        verification.get("evidence_quality", 0)
    )

    source_agreement = _safe_score(
        verification.get("source_agreement", 0)
    )
    source_reliability = _safe_score(
        verification.get("source_reliability", 0)
    )

    historical_reliability = _safe_score(
        verification.get("historical_reliability", 50)
    )

    effective_source_reliability = (
        source_reliability * 0.7
        + historical_reliability * 0.3
    )

    domain_risk = calculate_domain_risk(
        verification.get("claim", "")
    )

    if verdict == "SUPPORTED":
        base_score = (
            confidence * 0.45
            + evidence_quality * 0.25
            + source_agreement * 0.15
            + effective_source_reliability * 0.15
        )

        risk_penalty = domain_risk * 0.10
        score = base_score - risk_penalty

    elif verdict == "CONTRADICTED":
        base_score = (
            (100 - confidence) * 0.45
            + (100 - evidence_quality) * 0.25
            + (100 - source_agreement) * 0.15
            + (100 - effective_source_reliability) * 0.15
        )

        risk_penalty = domain_risk * 0.10
        score = base_score - risk_penalty

    else:
        score = 50

    return round(max(0, min(100, score)), 2)


def calculate_trust_score(verifications: list) -> float:
    """
    Calculate the overall trust score from all verified claims.
    """

    if not verifications:
        return 0

    claim_scores = [
        calculate_claim_score(verification)
        for verification in verifications
    ]

    overall_score = sum(claim_scores) / len(claim_scores)

    return round(overall_score, 2)