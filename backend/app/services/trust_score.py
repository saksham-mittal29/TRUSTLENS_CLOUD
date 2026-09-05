def calculate_claim_score(verification: dict) -> float:
    """
    Calculate a trust score for a single verified claim.

    The score considers:
    - verdict
    - confidence
    - evidence quality
    """

    verdict = verification.get("verdict", "UNCERTAIN")
    confidence = verification.get("confidence", 0)
    evidence_quality = verification.get("evidence_quality", 0)

    # Keep values within valid range
    confidence = max(0, min(100, confidence))
    evidence_quality = max(0, min(100, evidence_quality))

    if verdict == "SUPPORTED":
        # Strong evidence + high confidence = high trust
        score = (
            confidence * 0.7
            + evidence_quality * 0.3
        )

    elif verdict == "CONTRADICTED":
        # High-confidence contradiction should strongly reduce trust
        score = (
            (100 - confidence) * 0.7
            + (100 - evidence_quality) * 0.3
        )

    else:  # UNCERTAIN
        # Uncertain claims stay around the middle
        score = 50

    return round(score, 2)


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