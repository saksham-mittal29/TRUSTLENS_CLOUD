import os
import json

from dotenv import load_dotenv
from google import genai

load_dotenv()
def validate_verification(verification: dict, evidence: list):
    """
    Validate and normalize Gemini verification output.
    """

    if not isinstance(verification, dict):
        verification = {}

    verdict = verification.get("verdict", "UNCERTAIN")
    confidence = verification.get("confidence", 0)
    reason = verification.get("reason", "")
    evidence_quality = verification.get("evidence_quality", 0)
    relevant_sources = verification.get("relevant_sources", [])

    allowed_verdicts = {
        "SUPPORTED",
        "CONTRADICTED",
        "UNCERTAIN"
    }

    if verdict not in allowed_verdicts:
        verdict = "UNCERTAIN"

    try:
        confidence = int(confidence)
    except (ValueError, TypeError):
        confidence = 0

    confidence = max(0, min(100, confidence))

    try:
        evidence_quality = int(evidence_quality)
    except (ValueError, TypeError):
        evidence_quality = 0

    evidence_quality = max(0, min(100, evidence_quality))

    if not isinstance(reason, str):
        reason = str(reason)

    if not isinstance(relevant_sources, list):
        relevant_sources = []

    validated_sources = []

    for source in relevant_sources:
        try:
            source_number = int(source)

            if 1 <= source_number <= len(evidence):
                validated_sources.append(source_number)

        except (ValueError, TypeError):
            continue

    relevant_sources = list(dict.fromkeys(validated_sources))

    return {
        "verdict": verdict,
        "confidence": confidence,
        "reason": reason,
        "evidence_quality": evidence_quality,
        "relevant_sources": relevant_sources
    }

def verify_claim(claim: str, evidence: list):

    if not evidence:
        return {
            "verdict": "UNCERTAIN",
            "confidence": 0,
            "reason": "No evidence was found to evaluate this claim.",
            "evidence_quality": 0,
            "relevant_sources": []
        }

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY environment variable is not set"
        )

    client = genai.Client(api_key=api_key)

    evidence_text = ""

    for i, item in enumerate(evidence, 1):
        evidence_text += f"""
SOURCE {i}

Title:
{item.get("title", "")}

URL:
{item.get("url", "")}

Evidence:
{item.get("snippet", "")}

"""

    prompt = f"""
You are a factual claim verification system.

Your task is to determine whether the CLAIM is supported,
contradicted, or uncertain based ONLY on the provided evidence.

CLAIM:
{claim}

EVIDENCE:
{evidence_text}

Rules:

1. SUPPORTED:
   The evidence directly supports the claim.

2. CONTRADICTED:
   The evidence directly disagrees with the claim.

3. UNCERTAIN:
   The evidence is insufficient, ambiguous, irrelevant,
   or does not directly establish the claim.

Do not assume information that is not present in the evidence.

Return ONLY valid JSON in exactly this format:

{{
    "verdict": "SUPPORTED",
    "confidence": 95,
    "reason": "Short explanation based on the evidence.",
    "evidence_quality": 90,
    "relevant_sources": [1, 2, 3]
}}

Rules:

1. verdict must be exactly one of:
   - SUPPORTED
   - CONTRADICTED
   - UNCERTAIN

2. confidence must be an integer from 0 to 100.

3. evidence_quality must be an integer from 0 to 100.

4. evidence_quality measures how useful and trustworthy
   the provided evidence is for evaluating the claim.

Consider:
- Does the evidence directly address the claim?
- Do multiple sources agree?
- Does the evidence contain specific factual information?
- Do the sources appear credible?

Do not give a high evidence_quality merely because
a source mentions the same topic.

5. relevant_sources must contain the numbers of the
   evidence sources that actually help verify the claim.

For example, if sources 1, 2 and 4 support the claim:

"relevant_sources": [1, 2, 4]

If no sources provide useful evidence:

"relevant_sources": []

6. reason must briefly explain why the verdict was selected.

Do not include markdown.
Do not include ```json.
Return JSON only.

CLAIM:
{claim}
"""

    result = client.models.generate_content(
        model="gemini-3.7-flash",
        contents=prompt
    )

    text = result.text.strip()

    # Remove accidental markdown fences
    text = text.replace("```json", "").replace("```", "").strip()

    try:
        verification = json.loads(text)
    except json.JSONDecodeError:
        raise ValueError(
            f"Gemini returned invalid verification JSON: {text}"
        )

    return validate_verification(verification, evidence)