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
from fedcourtsai.pipeline.ingest import CorpusRow as IngestRow
from fedcourtsai.pipeline.ingest import CorpusSource, default_event
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


def test_opt_in_fixtures_take_their_own_docket_ids(tmp_path: Path) -> None:
    """An opt-in fixture adds a row; it never merges over a base-surface row.

    The base corpus is a measured statistical surface, and the corpus upsert
    latches rather than replaces — an opt-in case reusing a base docket id
    would silently rewrite that row's identity while its latched escalation
    columns survived, and the cell would provision from whichever snapshot is
    newer. The id-disjointness assertion is the rule; the behavioral half pins
    that opting in is purely additive.
    """
    base_ids = {case.case_id for case in fixture.FIXTURE_CASES}
    opt_ins = (fixture.MERITS_FIXTURE_CASE, fixture.CVSG_FIXTURE_CASE)
    assert {case.case_id for case in opt_ins}.isdisjoint(base_ids)

    db = fixture.build_fixture_corpus(tmp_path / "corpus.db")
    with corpus.connect(db) as conn:
        before = corpus.count(conn)
        base_application = corpus.get_row(conn, "scotus/306")
    added = fixture.add_merits_fixture(db)
    with corpus.connect(db) as conn:
        assert corpus.count(conn) == before + 1
        assert corpus.get_row(conn, "scotus/306") == base_application
        assert corpus.get_row(conn, added.case_id) is not None


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


def test_fixture_baseline_events_mirror_the_production_mint() -> None:
    """Every fixture case's baseline event is what discovery would mint for it.

    The fixture is a miniature, not a mock, so its event shape has to be the
    production rule's own answer — otherwise a case shaped like a real docket
    could carry a kind/stage pair the pipeline would never produce, and the
    offline cascade would prove a contract that does not exist. Pinned across
    the whole table because the fixture's `kind` keys on the *tolerant*
    application recognizer while `default_event` keys on the *strict* one: they
    agree on every spelling the fixture carries, and this is what keeps it so.
    """
    for case in fixture.FIXTURE_CASES:
        # `default_event` reads the ingestion-stage row; the fixture stores the
        # packed-corpus one. Project across the seam with the fields the mint
        # actually reads (court, docket number, identity, filing date, label).
        ingested = IngestRow(
            case_id=case.case_id,
            court=case.court,
            docket_id=str(case.docket),
            source=CorpusSource.live,
            docket_number=case.docket_number,
            case_name=case.case_name,
            date_filed=case.date_filed,
            disposition=case.disposition,
        )
        assert case.event() == default_event(ingested), case.case_id


def test_fixture_sets_the_scope_column_by_court(tmp_path: Path) -> None:
    """The build sets the derived scope column by the real rule: SCOTUS only."""
    db = fixture.build_fixture_corpus(tmp_path / "corpus.db")
    with corpus.connect(db) as conn:
        assert corpus.get_row(conn, "scotus/304").predict_eligible is True  # type: ignore[union-attr]
        # Court-of-appeals dockets — linked to SCOTUS or not — stay out of scope.
        assert corpus.get_row(conn, "ca9/102").predict_eligible is False  # type: ignore[union-attr]
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
