import pytest
from app.services.source_reliability_repository import (
    get_domain,
    get_or_create_source,
    update_source_reliability,
    get_historical_reliability,
)
from app.models import SourceReliability


def test_get_domain_normalization():
    assert get_domain("https://www.nature.com/articles/123") == "nature.com"
    assert get_domain("http://wikipedia.org/wiki/Paris") == "wikipedia.org"
    assert get_domain("invalid-url") == ""


def test_source_reliability_adaptive_update(db_session):
    test_domain = "pytest-source-test-domain.org"

    # Cleanup if exists
    db_session.query(SourceReliability).filter_by(domain=test_domain).delete()
    db_session.commit()

    try:
        # 1. Unseen domain default is 50.0
        initial_score = get_historical_reliability(db_session, test_domain)
        assert initial_score == 50.0

        # 2. Add supported evaluation
        source = update_source_reliability(db_session, test_domain, "SUPPORTED")
        db_session.commit()

        assert source.total_evaluations == 1
        assert source.supported_count == 1
        # Laplace: (1 + 0.5*0 + 1) / (1 + 2) * 100 = 2/3 * 100 = 66.67
        assert source.historical_reliability == 66.67

        # 3. Add contradicted evaluation
        source = update_source_reliability(db_session, test_domain, "CONTRADICTED")
        db_session.commit()

        assert source.total_evaluations == 2
        assert source.contradicted_count == 1
        # Laplace: (1 + 0.5*0 + 1) / (2 + 2) * 100 = 2/4 * 100 = 50.0
        assert source.historical_reliability == 50.0

    finally:
        db_session.query(SourceReliability).filter_by(domain=test_domain).delete()
        db_session.commit()
