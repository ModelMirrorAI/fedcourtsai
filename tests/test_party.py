"""Fixture-pinned tests for the party annotations (`pipeline.party`).

The annotations feed analytics cuts, so these fixtures are the specification
the same way the caption rules' are: a change that moves any of them is a new
rule version registered beside ``party-v1``, never a quiet retune of a label
someone has already published a count under. Two properties get the most
fixtures because they are the ones a reader is most likely to assume wrongly —
that the administration comes from the date and never from the officer the
caption names, and that the president flag is a name match rather than an
identification.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus, corpus_remote
from fedcourtsai.cli import _census_corpus_sha, app
from fedcourtsai.config import Settings
from fedcourtsai.corpus_ranged import RangedBackendError
from fedcourtsai.pipeline.party import (
    ADMINISTRATIONS,
    PARTY_RULE_VERSION,
    PARTY_RULES,
    administration_for,
    as_of_date,
    docket_stratum,
    party_annotations,
    party_census,
    party_rule,
    respondent_caption,
)
from fedcourtsai.schemas import Disposition

runner = CliRunner()

# A date safely inside each administration the live slice spans, so a fixture
# never rides an inauguration boundary except where that IS the fixture.
IN_TRUMP_45 = date(2019, 6, 1)
IN_BIDEN_46 = date(2022, 6, 1)
IN_TRUMP_47 = date(2025, 6, 1)


def _row(case_id: str, case_name: str, **kwargs: object) -> corpus.CorpusRow:
    """One live-slice SCOTUS row: `last_live_polled` is what puts it in the slice."""
    return corpus.CorpusRow(
        case_id=case_id,
        court="scotus",
        case_name=case_name,
        last_live_polled=date(2026, 9, 1),
        **kwargs,
    )


def test_the_federal_side_reads_both_halves_of_the_caption() -> None:
    """A sovereign is classified wherever it stands, not only as petitioner."""
    petitioner = party_annotations(_row("scotus/1", "United States v. Jane Doe"), IN_BIDEN_46)
    respondent = party_annotations(_row("scotus/2", "Jane Doe v. United States"), IN_BIDEN_46)
    both = party_annotations(
        _row("scotus/3", "Department of Homeland Security v. Merrick B. Garland, Attorney General"),
        IN_BIDEN_46,
    )
    neither = party_annotations(_row("scotus/4", "Jane Doe v. Acme Corp."), IN_BIDEN_46)
    assert petitioner.federal_party == "petitioner"
    assert respondent.federal_party == "respondent"
    assert both.federal_party == "both"
    assert neither.federal_party == "none"
    assert (petitioner.petitioner_class, petitioner.respondent_class) == ("federal", "private")
    assert (respondent.petitioner_class, respondent.respondent_class) == ("private", "federal")


def test_the_state_side_reads_both_halves_too() -> None:
    """The same composition over the state class, including both-sides cases."""
    petitioner = party_annotations(_row("scotus/1", "Oklahoma v. Victor Castro"), IN_BIDEN_46)
    respondent = party_annotations(
        _row("scotus/2", "Mica Martinez v. Christe Quick, Warden"), IN_BIDEN_46
    )
    both = party_annotations(_row("scotus/3", "California, et al. v. Texas, et al."), IN_BIDEN_46)
    assert petitioner.state_party == "petitioner"
    assert respondent.state_party == "respondent"
    assert both.state_party == "both"
    # A state-only case has no federal party, so it gets no administration:
    # stamping the date's president on it would invite a meaningless cross-tab.
    assert both.federal_party == "none"
    assert both.administration is None


def test_the_structured_petitioner_column_wins_over_the_caption_split() -> None:
    """`petitioner_title` is the rendering-independent read; the split is the fallback."""
    row = _row(
        "scotus/1",
        "Doe, Petitioner v. Jane Roe",
        petitioner_title="United States",
    )
    annotation = party_annotations(row, IN_BIDEN_46)
    assert annotation.petitioner_class == "federal"
    # No structured respondent column exists on either path, so that side is
    # always the split — and it is the split of the joined caption, not of the
    # structured column.
    assert respondent_caption(row) == "Jane Roe"


def test_a_single_party_caption_has_no_respondent_class() -> None:
    """`In re` annotates from one party; the missing side is null, never `private`."""
    annotation = party_annotations(_row("scotus/1", "In Re Michael Rocks-Macqueen"), IN_BIDEN_46)
    assert respondent_caption(_row("scotus/1", "In Re Michael Rocks-Macqueen")) is None
    assert annotation.respondent_class is None
    assert annotation.federal_party == "none"
    assert annotation.state_party == "none"


def test_the_administration_follows_the_date_not_the_officer_named() -> None:
    """The substitution scenario: one case, two as-of dates, two administrations.

    A federal officer is captioned in official capacity and the caption
    auto-substitutes on a transition, so the stored caption names whoever held
    the office when the row was last pulled. Both halves of this fixture are the
    *same* case as the corpus could hold it either side of 2021-01-20: the
    administration must track the date and be identical under both renderings.
    """
    before = _row("scotus/1", "Jane Doe v. Chad Wolf, Acting Secretary of Homeland Security")
    after = _row("scotus/1", "Jane Doe v. Alejandro Mayorkas, Secretary of Homeland Security")
    for row in (before, after):
        assert party_annotations(row, IN_TRUMP_45).administration == "trump-45"
        assert party_annotations(row, IN_BIDEN_46).administration == "biden-46"
        assert party_annotations(row, IN_TRUMP_47).administration == "trump-47"
        assert party_annotations(row, IN_BIDEN_46).federal_party == "respondent"


def test_the_administration_is_null_where_it_cannot_be_known() -> None:
    """Undated rows and pre-calendar dates answer null, never the nearest label."""
    row = _row("scotus/1", "Jane Doe v. United States")
    assert party_annotations(row, None).administration is None
    assert party_annotations(row, date(1975, 1, 1)).administration is None
    assert administration_for(None) is None
    assert administration_for(date(1975, 1, 1)) is None


def test_inauguration_day_attributes_to_the_incoming_administration() -> None:
    """The boundary rule, stated once and pinned: `start <= as_of`.

    The transfer happens at noon Eastern and we hold dates, not times, so the
    whole of inauguration day goes to the incoming administration.
    """
    assert administration_for(date(2021, 1, 19)) == "trump-45"
    assert administration_for(date(2021, 1, 20)) == "biden-46"
    assert administration_for(date(2025, 1, 20)) == "trump-47"
    # Two non-consecutive terms are two administrations, which is why the label
    # carries the presidency's ordinal rather than the surname alone.
    assert administration_for(date(2019, 6, 1)) == "trump-45"


def test_the_calendar_is_ascending_and_uniquely_labelled() -> None:
    """A calendar out of order or with a repeated label would misattribute silently."""
    starts = [admin.start for admin in ADMINISTRATIONS]
    assert starts == sorted(starts)
    assert len({admin.label for admin in ADMINISTRATIONS}) == len(ADMINISTRATIONS)


def test_a_president_named_in_personal_capacity_is_flagged_not_classified() -> None:
    """The personal-capacity family the official-capacity path deliberately excludes."""
    annotation = party_annotations(_row("scotus/1", "Donald J. Trump v. E. Jean Carroll"), None)
    assert annotation.named_president == "Trump"
    assert annotation.named_president_in_caption is True
    assert annotation.named_president_side == "petitioner"
    # Personal capacity: no office in the caption, so no federal party and no
    # administration — the flag is the only thing that fires.
    assert annotation.federal_party == "none"
    assert annotation.administration is None
    respondent_side = party_annotations(_row("scotus/2", "Joe Alter v. Donald J. Trump"), None)
    assert (respondent_side.named_president, respondent_side.named_president_side) == (
        "Trump",
        "respondent",
    )


def test_the_official_capacity_caption_flags_and_classifies() -> None:
    """A president sued in office is both a federal party and a named president."""
    annotation = party_annotations(
        _row("scotus/1", "Gwynne A. Wilcox v. Donald J. Trump, President of the United States"),
        IN_TRUMP_47,
    )
    assert annotation.federal_party == "respondent"
    assert annotation.administration == "trump-47"
    assert annotation.named_president == "Trump"


def test_the_president_flag_is_a_name_match_with_its_false_positives_pinned() -> None:
    """A private litigant of the same surname fires the flag; an entity does not.

    Pinned deliberately in both directions, because the flag's honest reading
    depends on it: no caption can distinguish a president from a namesake, so
    the flag screens rather than identifies, while requiring the surname to END
    the party's name segment keeps entities merely containing the word out.
    """
    namesake = party_annotations(
        _row("scotus/1", "Antwaun Bush v. City of Pittsburgh, Pennsylvania"), None
    )
    assert namesake.named_president == "Bush"
    entity = party_annotations(_row("scotus/2", "Bush Brothers & Co. v. Jane Doe"), None)
    assert entity.named_president is None
    assert entity.named_president_in_caption is False
    county = party_annotations(_row("scotus/3", "Clinton County Board v. Jane Doe"), None)
    assert county.named_president is None


def test_the_as_of_field_selects_which_date_the_cut_reads() -> None:
    """`filed` is arrival, `resolved` is the petition-stage resolution moment."""
    row = _row(
        "scotus/1",
        "Jane Doe v. United States",
        date_filed=date(2020, 11, 2),
        date_cert_denied=date(2021, 3, 1),
        date_decided=date(2024, 1, 1),
    )
    assert as_of_date(row, "filed") == date(2020, 11, 2)
    # The cert-stage date wins over `date_decided`, which carries termination
    # semantics and for a granted petition is the merits judgment months later.
    assert as_of_date(row, "resolved") == date(2021, 3, 1)
    assert party_annotations(row, as_of_date(row, "filed")).administration == "trump-45"
    assert party_annotations(row, as_of_date(row, "resolved")).administration == "biden-46"
    with pytest.raises(ValueError, match="unknown as-of field"):
        as_of_date(row, "argued")


def test_only_registered_rules_annotate() -> None:
    """An unregistered label raises rather than falling back to the current rule."""
    assert party_rule(PARTY_RULE_VERSION) is party_annotations
    assert set(PARTY_RULES) == {PARTY_RULE_VERSION}
    with pytest.raises(KeyError):
        party_rule("party-v9")


def test_the_docket_stratum_partitions_the_frame() -> None:
    """Every row lands in exactly one stratum, off its docket number alone."""
    assert docket_stratum(_row("scotus/1", "A v. B", docket_number="24-100")) == "paid-cert"
    assert docket_stratum(_row("scotus/2", "A v. B", docket_number="24-5001")) == "ifp-cert"
    assert docket_stratum(_row("scotus/3", "A v. B", docket_number="24A100")) == "application"
    assert docket_stratum(_row("scotus/4", "A v. B", docket_number="22O141")) == "other"
    assert docket_stratum(_row("scotus/5", "A v. B")) == "other"


def _census_corpus(db: Path) -> None:
    """The census fixture frame: three administrations, three strata, every gap."""
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                _row(
                    "scotus/1",
                    "Jane Doe v. United States",
                    docket_number="18-100",
                    date_filed=date(2019, 6, 1),
                    date_cert_denied=date(2022, 6, 1),
                    disposition=Disposition.denied,
                ),
                _row(  # pending: no resolution date, so `resolved` cannot place it
                    "scotus/2",
                    "United States v. Acme Corp.",
                    docket_number="24-200",
                    date_filed=date(2025, 6, 1),
                ),
                _row(
                    "scotus/3",
                    "Oklahoma v. Victor Castro",
                    docket_number="21-300",
                    date_filed=date(2022, 6, 1),
                    date_cert_denied=date(2022, 12, 1),
                    disposition=Disposition.denied,
                ),
                _row(  # undated, single-party, and the frame's only IFP row
                    "scotus/4",
                    "In Re Michael Rocks-Macqueen",
                    docket_number="24-5001",
                    disposition=Disposition.denied,
                ),
                _row(  # an application, with a president in office in the caption
                    "scotus/7",
                    "Donald J. Trump, President of the United States v. Jane Doe",
                    docket_number="25A100",
                    date_filed=date(2025, 6, 1),
                    date_decided=date(2025, 7, 1),
                    disposition=Disposition.denied,
                ),
                _row(  # the legacy sampled block: counted, never annotated
                    "scotus/5",
                    "John Roe v. United States",
                    docket_number="18-5010",
                    date_filed=date(2019, 6, 1),
                    disposition=Disposition.denied,
                    sample_weight=10,
                ),
                corpus.CorpusRow(  # not live-slice: outside the frame entirely
                    case_id="scotus/6",
                    court="scotus",
                    case_name="Jane Poe v. United States",
                    docket_number="18-400",
                    date_filed=date(2019, 6, 1),
                ),
            ],
        )


def test_the_census_counts_the_unweighted_live_slice(tmp_path: Path) -> None:
    """The frame is the live slice's unweighted rows, with every gap counted.

    The sampled block is excluded rather than mixed in — stored one row in ten,
    it would understate its stratum tenfold in exactly the cells it fills — and
    is reported whole, in the same window-and-stratum cells as the frame, so the
    coverage gap is legible where the federal counts are read.
    """
    db = tmp_path / "corpus.db"
    _census_corpus(db)
    with corpus.connect(db) as conn:
        census = party_census(conn, as_of_field="filed")
    assert census.rule_version == "party-v1"
    assert census.as_of_field == "filed"
    assert (census.rows, census.sampled_excluded) == (5, 1)
    assert (census.single_party, census.undated, census.pending) == (1, 1, 1)
    federal = {cell.side: cell.n for cell in census.federal_party}
    assert federal == {"both": 0, "petitioner": 2, "respondent": 1, "none": 2}
    state = {cell.side: cell.n for cell in census.state_party}
    assert state["petitioner"] == 1
    by_admin = {
        (cell.federal_party, cell.administration, cell.stratum): cell.n
        for cell in census.federal_by_administration
    }
    # Two federal petitioners share the trump-47 window and split by stratum:
    # pooling them would compare a cert docket with an application docket.
    assert by_admin == {
        ("petitioner", "trump-47", "paid-cert"): 1,
        ("petitioner", "trump-47", "application"): 1,
        ("respondent", "trump-45", "paid-cert"): 1,
    }
    frame = {
        (cell.administration, cell.stratum): (cell.rows, cell.sampled_excluded)
        for cell in census.frame_by_administration
    }
    # Every frame row is dated and stratified, federal party or not; the excluded
    # block rides the same cells, and the undated row is its own.
    assert frame == {
        ("trump-45", "paid-cert"): (1, 0),
        ("trump-45", "ifp-cert"): (0, 1),
        ("biden-46", "paid-cert"): (1, 0),
        ("trump-47", "paid-cert"): (1, 0),
        ("trump-47", "application"): (1, 0),
        (None, "ifp-cert"): (1, 0),
    }
    assert [cell.president for cell in census.named_president] == ["Trump"]


def test_the_census_stamp_changes_with_the_date_convention(tmp_path: Path) -> None:
    """One corpus, two conventions, two correct answers — which is why it is stamped."""
    db = tmp_path / "corpus.db"
    _census_corpus(db)
    with corpus.connect(db) as conn:
        filed = party_census(conn, as_of_field="filed")
        resolved = party_census(conn, as_of_field="resolved")
    assert {
        (c.federal_party, c.administration, c.stratum): c.n for c in filed.federal_by_administration
    } == {
        ("petitioner", "trump-47", "paid-cert"): 1,
        ("petitioner", "trump-47", "application"): 1,
        ("respondent", "trump-45", "paid-cert"): 1,
    }
    # scotus/1 was filed under trump-45 and denied under biden-46; scotus/2 is
    # pending, so under `resolved` it leaves its window for the unattributed
    # cell — the right-censoring `pending` counts, not a case that vanished.
    assert {
        (c.federal_party, c.administration, c.stratum): c.n
        for c in resolved.federal_by_administration
    } == {
        ("petitioner", None, "paid-cert"): 1,
        ("petitioner", "trump-47", "application"): 1,
        ("respondent", "biden-46", "paid-cert"): 1,
    }
    assert (resolved.undated, resolved.pending) == (2, 1)
    assert filed.pending == resolved.pending
    with pytest.raises(ValueError, match="unknown as-of field"), corpus.connect(db) as conn:
        party_census(conn, as_of_field="argued")


def test_the_command_prints_the_census_with_its_vintage(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The report's shape: JSON on stdout, the human cut plus the corpus vintage on stderr."""
    corpus_root = tmp_path / "corpus"
    _census_corpus(corpus.corpus_db_path(corpus_root))
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(corpus_root))
    result = runner.invoke(app, ["party-census", "--as-of", "filed"])
    assert result.exit_code == 0, result.output
    assert (
        "party census (party-v1 over caption-v2, as-of filed): 5 unweighted live-slice row(s)"
        in result.stderr
    )
    assert "1 sampled row(s) excluded" in result.stderr
    # The vintage is on the banner, not only in the JSON: a count read off a
    # stale blob is a different number.
    assert "corpus latest pull never pulled" in result.stderr
    assert "frame trump-45 ifp-cert: rows=0 sampled-excluded=1" in result.stderr
    assert "federal_party respondent x trump-45 paid-cert: n=1" in result.stderr
    assert '"rule_version":"party-v1"' in result.stdout
    assert '"caption_rule_version":"caption-v2"' in result.stdout


def test_the_command_refuses_an_unregistered_label(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A rule or convention this process cannot produce is an error, not a fallback."""
    corpus_root = tmp_path / "corpus"
    _census_corpus(corpus.corpus_db_path(corpus_root))
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(corpus_root))
    unknown_rule = runner.invoke(
        app, ["party-census", "--as-of", "filed", "--rule-version", "party-v9"]
    )
    assert unknown_rule.exit_code == 2
    assert "unregistered party rule" in unknown_rule.stderr
    unknown_field = runner.invoke(app, ["party-census", "--as-of", "argued"])
    assert unknown_field.exit_code == 2
    assert "unknown --as-of" in unknown_field.stderr


def _pointer(sha: str) -> str:
    """A well-formed committed index pointer naming ``sha``."""
    return json.dumps(
        {"key": f"index/sha256/{sha}", "schema_version": "1.0", "sha256": sha, "size": 7}
    )


def test_the_provenance_digest_names_the_blob_each_backend_actually_reads(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The one digest three censuses stamp, over every branch it has.

    Two of those censuses are freeze-record inputs, so a digest that silently
    changed meaning — the committed pointer read where the override governs, or
    a malformed pointer blanked instead of raised — would corrupt the record
    rather than fail. The branches are pinned here because one helper now
    carries all three commands.
    """
    db_path = tmp_path / "corpus.db"
    db_path.write_bytes(b"corpus!")
    local_sha, _ = corpus_remote.digest_file(db_path)
    committed = "a" * 64
    override = "b" * 64
    corpus_remote.pointer_path_for(db_path).write_text(_pointer(committed))

    monkeypatch.setenv("FEDCOURTS_CORPUS_POINTER", _pointer(override))
    local = Settings(corpus_backend="local")
    assert _census_corpus_sha(local, db_path) == local_sha  # the file, not the pointer
    # The override governs every ranged READ path, so it must govern the digest
    # too: a stamp naming the committed blob while the override's blob was read
    # is the one failure a freeze record cannot recover from.
    assert _census_corpus_sha(Settings(corpus_backend="ranged"), db_path) == override

    monkeypatch.delenv("FEDCOURTS_CORPUS_POINTER")
    assert _census_corpus_sha(Settings(corpus_backend="ranged"), db_path) == committed

    # A MISSING committed pointer is excused with an empty digest; a MALFORMED
    # one raises rather than blanking the field.
    bare = tmp_path / "bare" / "corpus.db"
    bare.parent.mkdir()
    bare.write_bytes(b"corpus!")
    assert _census_corpus_sha(Settings(corpus_backend="ranged"), bare) == ""
    corpus_remote.pointer_path_for(bare).write_text("{not json")
    with pytest.raises(RangedBackendError):
        _census_corpus_sha(Settings(corpus_backend="ranged"), bare)


def test_the_command_fails_loud_without_a_corpus(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """No corpus is an error here: a census over nothing would print zeros as findings."""
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "empty"))
    result = runner.invoke(app, ["party-census", "--as-of", "filed"])
    assert result.exit_code == 1
    assert "the corpus database is missing" in result.stderr
