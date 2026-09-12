import sys
from pathlib import Path
import csv
import json

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent)
)

from app.services.claim_verifier import verify_claim


BASE_DIR = Path(__file__).resolve().parent

CACHE_FILE = BASE_DIR / "evidence_cache.json"
OUTPUT_FILE = BASE_DIR / "results.csv"

START_ROW = 6
END_ROW = 10


def run_evaluation():
    with CACHE_FILE.open("r", encoding="utf-8") as file:
        cache = json.load(file)

    results = []

    # Load existing results
    if OUTPUT_FILE.exists():
        with OUTPUT_FILE.open(
            "r",
            encoding="utf-8"
        ) as file:
            reader = csv.DictReader(file)
            results = list(reader)

    selected = cache[START_ROW - 1:END_ROW]

    for row_number, item in enumerate(
        selected,
        start=START_ROW
    ):
        claim = item["claim"]
        ground_truth = item["ground_truth"]
        evidence = item["evidence"]

        print(f"[{row_number}] Verifying: {claim}")

        try:
            verification = verify_claim(
                claim,
                evidence
            )

            prediction = verification.get(
                "verdict",
                "UNCERTAIN"
            )

            results.append({
                "id": item["id"],
                "claim": claim,
                "ground_truth": ground_truth,
                "prediction": prediction,
                "confidence": verification.get(
                    "confidence",
                    0
                ),
                "evidence_quality": verification.get(
                    "evidence_quality",
                    0
                ),
                "source_agreement": verification.get(
                    "source_agreement",
                    0
                ),
                "source_reliability": verification.get(
                    "source_reliability",
                    0
                ),
                "error": "",
            })

            print(
                f"    Ground truth: {ground_truth}"
            )
            print(
                f"    Prediction:   {prediction}"
            )

        except Exception as error:
            print(f"    ERROR: {error}")

            results.append({
                "id": item["id"],
                "claim": claim,
                "ground_truth": ground_truth,
                "prediction": "ERROR",
                "confidence": 0,
                "evidence_quality": 0,
                "source_agreement": 0,
                "source_reliability": 0,
                "error": str(error),
            })

    with OUTPUT_FILE.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "id",
                "claim",
                "ground_truth",
                "prediction",
                "confidence",
                "evidence_quality",
                "source_agreement",
                "source_reliability",
                "error",
            ],
        )

        writer.writeheader()
        writer.writerows(results)

    print()
    print(f"Results saved to: {OUTPUT_FILE}")
    print(f"Total results: {len(results)}")


if __name__ == "__main__":
    run_evaluation()
