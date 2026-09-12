import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent)
)

import csv

from app.services.evidence_search import search_evidence
from app.services.claim_verifier import verify_claim


BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "dataset.csv"
OUTPUT_FILE = BASE_DIR / "results.csv"


def run_evaluation():
    results = []

    with INPUT_FILE.open("r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row_number, row in enumerate(reader, start=1):
            if row_number > 5:
                break

            claim = row["claim"]
            ground_truth = row["ground_truth"]

            print(f"[{row_number}] Verifying: {claim}")

            try:
                evidence = search_evidence(claim)

                verification = verify_claim(
                    claim,
                    evidence
                )

                prediction = verification.get(
                    "verdict",
                    "UNCERTAIN"
                )

                results.append({
                    "id": row["id"],
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
                    "id": row["id"],
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

    successful = sum(
        1 for result in results
        if result["prediction"] != "ERROR"
    )

    errors = sum(
        1 for result in results
        if result["prediction"] == "ERROR"
    )

    print()
    print(f"Results saved to: {OUTPUT_FILE}")
    print(f"Total claims: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Errors: {errors}")


if __name__ == "__main__":
    run_evaluation()
