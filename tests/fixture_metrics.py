"""A small statpack for the tests that provision cert cells through the cascade.

Written under a test's own temporary directory rather than read off the
committed ``metrics/statpack.json``, so a cascade test's frozen cert anchor
depends neither on the working directory nor on whichever build the last
metrics refresh committed. Every band of the live salience version carries a
prior-Term risk-set rate in every Term it lists, so a frozen band pools.
"""

from __future__ import annotations

from pathlib import Path

from fedcourtsai.pipeline.salience import SALIENCE_VERSION, scorer
from fedcourtsai.schemas import BaseRateBucket, StatPack, StatPackTerm, StatPackTermSegment
from fedcourtsai.serialize import write_json

#: The Terms the fixture pack lists: every fixture docket's Term has priors here.
FIXTURE_TERMS = tuple(range(2015, 2027))

#: The risk-set rate every band carries in every Term.
FIXTURE_BAND_RATE = 0.05


def fixture_statpack() -> StatPack:
    """The pack :func:`fixture_metrics_root` writes."""
    bands = scorer(SALIENCE_VERSION).bands
    return StatPack(
        corpus_rows=1,
        terms=[
            StatPackTerm(
                term=term,
                base_rates=BaseRateBucket(),
                salience_version=SALIENCE_VERSION,
                segments=[
                    StatPackTermSegment(
                        band=band,
                        prefix_est_grant_rate=FIXTURE_BAND_RATE,
                        prefix_weighted_resolved=100,
                        est_grant_rate=FIXTURE_BAND_RATE,
                        weighted_resolved=100,
                    )
                    for band in bands
                ],
            )
            for term in FIXTURE_TERMS
        ],
    )


def fixture_metrics_root(base: Path) -> Path:
    """Write :func:`fixture_statpack` to ``base/metrics/statpack.json``; return that directory."""
    root = base / "metrics"
    write_json(root / "statpack.json", fixture_statpack())
    return root
