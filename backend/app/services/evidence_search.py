from ddgs import DDGS
from urllib.parse import urlparse


def calculate_source_reliability(url: str) -> int:
    """
    Estimate source reliability from the source domain.
    Returns a score from 0 to 100.
    """

    try:
        domain = urlparse(url).netloc.lower()
    except Exception:
        return 0

    domain = domain.replace("www.", "")

    if domain.endswith(".gov"):
        return 95

    if domain.endswith(".edu"):
        return 90

    high_reliability_domains = {
        "nasa.gov",
        "who.int",
        "un.org",
        "nature.com",
        "science.org",
        "reuters.com",
        "apnews.com",
        "britannica.com",
    }

    if domain in high_reliability_domains:
        return 90

    if domain == "wikipedia.org":
        return 75

    if domain.endswith(".org"):
        return 70

    if domain.endswith(".com"):
        return 60

    return 50


def search_evidence(query: str):
    results = []

    try:
        with DDGS() as ddgs:
            search_results = ddgs.text(
                query,
                max_results=5
            )

            for result in search_results:
                url = result.get("href", "")
                results.append({
                    "title": result.get("title"),
                    "url": url,
                    "snippet": result.get("body"),
                    "source_reliability": calculate_source_reliability(url)
                })

    except Exception as e:
        print(f"Evidence search error: {e}")

    return results