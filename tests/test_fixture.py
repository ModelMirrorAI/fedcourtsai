"""The synthetic fixture corpus module and the read seams it backs.

Proves the fixture builds deterministically, is a consistent miniature across
courts, and backs ``corpus.retrieve_priors`` and ``open-events`` offline. The CLI
``provision-snapshot`` and ``query`` surfaces run against the same fixture in
``test_cli_provision`` / ``test_cli_query`` via the shared ``fixture_corpus``
fixture (no remote configured).
"""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from fedcourtsai import corpus, fixture
from fedcourtsai.cli import app
from tests.conftest import FixtureCorpus

runner = CliRunner()


# --- the fixture itself --------------------------------------------------------


def test_fixture_builds_deterministically(tmp_path: Path) -> None:
    """Two builds over fresh paths are byte-identical (no clock, no randomness)."""
    first = fixture.build_fixture_corpus(tmp_path / "a.db")
    second = fixture.build_fixture_corpus(tmp_path / "b.db")
    assert first.read_bytes() == second.read_bytes()


def test_fixture_overwrites_existing_db(tmp_path: Path) -> None:
    """Rebuilding over an existing file starts fresh — content is the fixture alone."""
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [corpus.CorpusRow(case_id="zz9/9", court="zz9")])
    fixture.build_fixture_corpus(db)
    with corpus.connect(db) as conn:
        assert corpus.get_row(conn, "zz9/9") is None
        assert corpus.count(conn) == len(fixture.FIXTURE_CASES)


def test_fixture_spans_courts_with_mixed_resolution(tmp_path: Path) -> None:
    """A faithful miniature: ≥2 courts, a mix of resolved and open, all consistent."""
    db = fixture.build_fixture_corpus(tmp_path / "corpus.db")
    with corpus.connect(db) as conn:
        rows = list(corpus.iter_rows(conn))
        courts = {r.court for r in rows}
        resolved = [r for r in rows if r.disposition is not None]
        open_ = [r for r in rows if r.disposition is None]
        assert len(courts) >= 2
        assert resolved and open_  # both kinds present
        # Every case carries exactly one snapshot and one event whose resolved
        # flag tracks the row's disposition — the three stores stay in step.
        assert corpus.snapshot_count(conn) == len(rows)
        for row in rows:
            assert corpus.latest_snapshot(conn, row.case_id) is not None
            (event,) = corpus.events_for_case(conn, row.case_id)
            assert event.resolved == (row.disposition is not None)


def test_fixture_latches_originating_court_eligible(tmp_path: Path) -> None:
    """The build runs the real eligibility latch: a SCOTUS link pulls its CoA docket in."""
    db = fixture.build_fixture_corpus(tmp_path / "corpus.db")
    with corpus.connect(db) as conn:
        # ca9/102 is in scope only because scotus/304 links back to it.
        assert corpus.get_row(conn, "ca9/102").predict_eligible is True  # type: ignore[union-attr]
        # An unlinked court-of-appeals docket stays out of scope.
        assert corpus.get_row(conn, "ca9/101").predict_eligible is False  # type: ignore[union-attr]


# --- offline read seams against the fixture ------------------------------------


def test_retrieve_priors_offline(fixture_corpus: FixtureCorpus) -> None:
    """corpus.retrieve_priors ranks resolved priors by judge overlap then recency."""
    with corpus.connect(fixture_corpus.db_path) as conn:
        priors = corpus.retrieve_priors(conn, corpus.PriorQuery(court="ca9", judges=["smith"]))
    # Both ca9/101 and ca9/102 share judge smith; ca9/102 decided later leads, and
    # the open ca9/103 is excluded by the resolved-only default.
    assert [p.case_id for p in priors] == ["ca9/102", "ca9/101"]


def test_open_events_offline(fixture_corpus: FixtureCorpus) -> None:
    """open-events lists a case's unresolved events and nothing for a resolved one."""
    open_case = runner.invoke(app, ["open-events", "--court", "scotus", "--docket", "305"])
    assert open_case.exit_code == 0, open_case.output
    assert open_case.stdout.split() == ["evt-petition-disposition"]
    # A resolved case has no open events.
    resolved_case = runner.invoke(app, ["open-events", "--court", "ca9", "--docket", "101"])
    assert resolved_case.exit_code == 0, resolved_case.output
    assert resolved_case.stdout.strip() == ""
