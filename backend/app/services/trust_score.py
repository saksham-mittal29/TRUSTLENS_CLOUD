def calculate_trust_score(results: list):
    if not results:
        return 0

    total_score = 0
    valid_results = 0

    for result in results:
        verdict = result.get("verdict", "").upper()
        confidence = result.get("confidence", 0)

        if verdict == "SUPPORTED":
            score = confidence

        elif verdict == "CONTRADICTED":
            score = 100 - confidence

        else:
            score = 50

        total_score += score
        valid_results += 1

    if valid_results == 0:
        return 0

    return round(total_score / valid_results)