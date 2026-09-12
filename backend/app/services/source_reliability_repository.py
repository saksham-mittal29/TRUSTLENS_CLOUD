from urllib.parse import urlparse

from sqlalchemy.orm import Session

from app.models import SourceReliability


def get_domain(url: str) -> str:
    """
    Extract a normalized domain from a URL.
    """
    try:
        domain = urlparse(url).netloc.lower()
        return domain.replace("www.", "")
    except Exception:
        return ""


def get_or_create_source(
    db: Session,
    domain: str
) -> SourceReliability:
    """
    Get an existing source reliability record or create one.
    """

    source = (
        db.query(SourceReliability)
        .filter(SourceReliability.domain == domain)
        .first()
    )

    if source:
        return source

    source = SourceReliability(
        domain=domain,
        total_evaluations=0,
        supported_count=0,
        contradicted_count=0,
        uncertain_count=0,
        historical_reliability=50.0,
    )

    db.add(source)
    db.flush()

    return source


def update_source_reliability(
    db: Session,
    domain: str,
    verdict: str
) -> SourceReliability:
    """
    Update the historical reliability of a source.
    """

    source = get_or_create_source(db, domain)

    source.total_evaluations += 1

    if verdict == "SUPPORTED":
        source.supported_count += 1

    elif verdict == "CONTRADICTED":
        source.contradicted_count += 1

    elif verdict == "UNCERTAIN":
        source.uncertain_count += 1

    source.historical_reliability = round(
        (
            source.supported_count
            + 0.5 * source.uncertain_count
            + 1
        )
        / (source.total_evaluations + 2)
        * 100,
        2
    )

    db.flush()

    return source


def get_historical_reliability(
    db: Session,
    domain: str
) -> float:
    """
    Get the historical reliability of a source.

    Unknown sources receive the neutral baseline of 50.
    """

    source = (
        db.query(SourceReliability)
        .filter(SourceReliability.domain == domain)
        .first()
    )

    if not source:
        return 50.0

    return source.historical_reliability

