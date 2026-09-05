from ddgs import DDGS


def search_evidence(query: str):
    results = []

    try:
        with DDGS() as ddgs:
            search_results = ddgs.text(
                query,
                max_results=5
            )

            for result in search_results:
                results.append({
                    "title": result.get("title"),
                    "url": result.get("href"),
                    "snippet": result.get("body")
                })

    except Exception as e:
        print(f"Evidence search error: {e}")

    return results