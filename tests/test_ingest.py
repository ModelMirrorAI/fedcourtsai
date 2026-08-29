from datetime import date, timedelta
from enum import Enum
from pathlib import Path
from types import UnionType
from typing import Any, Union, get_args, get_origin

import pytest

from fedcourtsai import corpus
from fedcourtsai.pipeline.ingest import (
    CorpusRow as IngestCorpusRow,
)
from fedcourtsai.pipeline.ingest import (
    CorpusSource,
    default_event,
    from_api_docket,
    from_bulk_row,
    is_predict_eligible,
    merge_rows,
    normalize_disposition,
    to_corpus_row,
    upsert_to_corpus,
)
from fedcourtsai.schemas import Disposition, EventKind

# Equivalent facts about one docket, shaped the way each upstream source delivers
# them: the API as a JSON object (court as a hyperlink, panel as nested judges),
# the bulk export as a flat CSV row (strings, pipe-delimited lists).
API_DOCKET = {
    "id": 64512345,
    "court": "https://www.courtlistener.com/api/rest/v4/courts/ca9/",
    "docket_number": "21-55555",
    "case_name": "Doe v. Roe",
    "date_filed": "2021-03-01",
    "date_terminated": "2022-06-15",
    "nature_of_suit": "Civil Rights",
    "panel": [
        {"name_full": "Jane Smith", "seniority": "active"},
        {"name_full": "Alan Lee", "seniority": "senior"},
    ],
    "parties": [{"name": "United States"}, {"name": "Jane Roe"}],
    "attorneys": [{"name": "A. Counsel"}],
    "disposition": "Motion granted in part and denied in part",
    "precedential_status": "Published",
    "citation_count": 5,
    "citations": ["12 F.4th 100"],
}

# The same facts as the bulk export delivers them: flat CSV strings, and the
# multi-valued siblings already shaped by the staged join — a resolved panel JSON
# and the `;`/JSON-array name lists the join serves.
BULK_ROW = {
    "id": "64512345",
    "court_id": "ca9",
    "docket_number": "21-55555",
    "case_name": "Doe v. Roe",
    "date_filed": "2021-03-01",
    "date_terminated": "2022-06-15",
    "nature_of_suit": "Civil Rights",
    "judges": "Alan Lee|Jane Smith",
    "panel": '[{"name": "Jane Smith", "seniority": "active"}, '
    '{"name": "Alan Lee", "seniority": "senior"}]',
    "parties": '["Jane Roe", "United States"]',
    "attorneys": '["A. Counsel"]',
    "disposition": "Motion granted in part and denied in part",
    "precedential_status": "Published",
    "citation_count": "5",
    "citations": "12 F.4th 100",
}


def test_api_and_bulk_normalize_to_same_row() -> None:
    api = from_api_docket(API_DOCKET)
    bulk = from_bulk_row(BULK_ROW)
    # The whole point of the shared core: identical apart from the source tag.
    assert api.model_dump(exclude={"source"}) == bulk.model_dump(exclude={"source"})
    assert api.source == CorpusSource.api
    assert bulk.source == CorpusSource.bulk


def test_normalized_fields() -> None:
    row = from_api_docket(API_DOCKET)
    assert row.case_id == "ca9/64512345"
    assert row.court == "ca9"
    assert row.docket_id == 64512345
    assert row.date_filed == date(2021, 3, 1)
    assert row.date_decided == date(2022, 6, 15)
    assert row.disposition == Disposition.granted_in_part
    assert row.nature_of_suit == "Civil Rights"
    assert row.judges == ["Alan Lee", "Jane Smith"]  # sorted, deduplicated
    assert row.citations == ["12 F.4th 100"]
    # Enriched sibling facts: structured panel (name + seniority), parties, attorneys,
    # and the opinion-cluster scalars.
    assert row.panel == [
        corpus.PanelMember(name="Jane Smith", seniority="active"),
        corpus.PanelMember(name="Alan Lee", seniority="senior"),
    ]
    assert row.parties == ["Jane Roe", "United States"]  # sorted, deterministic
    assert row.attorneys == ["A. Counsel"]
    assert row.precedential_status == "Published"
    assert row.citation_count == 5


def test_panel_names_fold_into_judges_when_free_text_blank() -> None:
    # A bulk row whose only judge signal is the resolved panel still fills `judges`.
    row = from_bulk_row(
        {"id": "1", "court_id": "ca9", "panel": '[{"name": "Pat Quinn"}, {"name": "Dana Vu"}]'}
    )
    assert row.judges == ["Dana Vu", "Pat Quinn"]
    assert [m.name for m in row.panel] == ["Pat Quinn", "Dana Vu"]
    assert row.panel[0].seniority is None  # absent in the directory → None


def test_court_id_from_url_and_field_agree() -> None:
    assert from_api_docket(API_DOCKET).court == from_bulk_row(BULK_ROW).court == "ca9"


def test_missing_court_is_rejected() -> None:
    with pytest.raises(ValueError, match="court"):
        from_api_docket({"id": 1})


def test_blank_optionals_become_none() -> None:
    row = from_bulk_row({"id": "7", "court_id": "ca1", "date_filed": "", "nature_of_suit": ""})
    assert row.date_filed is None
    assert row.date_decided is None
    assert row.disposition is None
    assert row.nature_of_suit is None
    assert row.judges == []
    assert row.citations == []
    assert row.docket_number == ""


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Granted", Disposition.granted),
        ("DENIED", Disposition.denied),
        ("granted in part", Disposition.granted_in_part),
        ("gvr", Disposition.gvr),  # the resolver's gvr value round-trips through here
        ("The petition was GVR'd", Disposition.gvr),
        ("Petition dismissed", Disposition.dismissed),
        ("Withdrawn by appellant", Disposition.withdrawn),
        ("affirmed", Disposition.other),
        ("", None),
        (None, None),
    ],
)
def test_normalize_disposition(raw: str | None, expected: Disposition | None) -> None:
    assert normalize_disposition(raw) == expected


def test_cert_stage_dates_extracted_identically_from_api_and_bulk() -> None:
    # Upstream carries the petition-stage decision as dates on the docket; both
    # channels hand the raw record through, so the mapping is source-agnostic.
    api = from_api_docket(
        {"id": 9, "court_id": "scotus", "docket_number": "22-451", "date_cert_denied": "2023-01-09"}
    )
    bulk = from_bulk_row(
        {
            "id": "9",
            "court_id": "scotus",
            "docket_number": "22-451",
            "date_cert_denied": "2023-01-09",
        }
    )
    assert api.model_dump(exclude={"source"}) == bulk.model_dump(exclude={"source"})
    assert api.date_cert_denied == date(2023, 1, 9)
    assert api.date_cert_granted is None
    # The date is the label: a denial date resolves the petition as denied.
    assert api.disposition == Disposition.denied
    # And the projection carries both dates onto the storage row.
    stored = to_corpus_row(api)
    assert stored.date_cert_denied == date(2023, 1, 9)
    assert stored.date_cert_granted is None
    assert stored.disposition == Disposition.denied


def test_cert_grant_date_wins_and_derives_granted() -> None:
    # A granted-then-disposed petition (incl. a GVR) was granted at the petition
    # stage, so the grant date wins when both cert dates are present.
    row = from_api_docket(
        {
            "id": 10,
            "court_id": "scotus",
            "date_cert_granted": "2022-10-03",
            "date_cert_denied": "2023-06-30",
        }
    )
    assert row.disposition == Disposition.granted
    assert row.date_cert_granted == date(2022, 10, 3)
    assert row.date_cert_denied == date(2023, 6, 30)


def test_textual_disposition_wins_over_cert_date_derivation() -> None:
    row = from_api_docket(
        {
            "id": 11,
            "court_id": "scotus",
            "disposition": "Petition dismissed",
            "date_cert_denied": "2023-01-09",
        }
    )
    assert row.disposition == Disposition.dismissed


def test_cert_dates_never_derive_a_disposition_off_scotus() -> None:
    # Defensive: only SCOTUS dockets read the petition-stage dates as a label;
    # the dates themselves are still stored faithfully.
    row = from_api_docket({"id": 12, "court_id": "ca9", "date_cert_denied": "2023-01-09"})
    assert row.disposition is None
    assert row.date_cert_denied == date(2023, 1, 9)


def test_merge_rows_last_wins() -> None:
    stale = from_bulk_row({**BULK_ROW, "nature_of_suit": "old"})
    fresh = from_api_docket(API_DOCKET)
    merged = merge_rows([stale, fresh])
    assert len(merged) == 1
    assert merged[0].nature_of_suit == "Civil Rights"
    assert merged[0].source == CorpusSource.api


def test_predict_eligibility_rule_is_scotus_only() -> None:
    # v1 prediction-scope rule: a SCOTUS docket is in-scope; a court of appeals
    # docket is not (until a later rule widens to the case's lower-court docket).
    scotus = from_api_docket({"id": 7, "court_id": "scotus"})
    ca9 = from_api_docket({"id": 8, "court_id": "ca9"})
    assert is_predict_eligible(scotus) is True
    assert is_predict_eligible(ca9) is False


def test_ingestion_sets_predict_eligible_for_scotus_only(tmp_path: Path) -> None:
    # The rule fires identically on either source (both project via to_corpus_row).
    assert to_corpus_row(from_api_docket({"id": 7, "court_id": "scotus"})).predict_eligible is True
    assert to_corpus_row(from_bulk_row({"id": "8", "court_id": "ca9"})).predict_eligible is False

    db = corpus.corpus_db_path(tmp_path)
    upsert_to_corpus(db, [from_bulk_row({"id": "7", "court_id": "scotus"})])
    upsert_to_corpus(db, [from_api_docket({"id": "8", "court_id": "ca9"})])
    with corpus.connect(db) as conn:
        scotus = corpus.get_row(conn, "scotus/7")
        ca9 = corpus.get_row(conn, "ca9/8")
    assert scotus is not None and scotus.predict_eligible is True
    assert ca9 is not None and ca9.predict_eligible is False


def test_originating_link_extracted_from_api_and_bulk() -> None:
    # REST nests the lower-court link (court hyperlink + originating-court-info),
    # so pull carries the full join key.
    api = from_api_docket(
        {
            "id": 1,
            "court_id": "scotus",
            "appeal_from": "https://www.courtlistener.com/api/rest/v4/courts/ca9/",
            "originating_court_information": {"docket_number": "21-35466"},
        }
    )
    assert api.originating_court == "ca9"
    assert api.originating_docket_number == "21-35466"

    # Bulk carries `appeal_from_id` (the court) but not the lower-court docket
    # number (CourtListener publishes no originating-court-info bulk table).
    bulk = from_bulk_row({"id": "2", "court_id": "scotus", "appeal_from_id": "ca9"})
    assert bulk.originating_court == "ca9"
    assert bulk.originating_docket_number is None

    # No link at all → both blank.
    bare = from_api_docket({"id": 3, "court_id": "scotus"})
    assert bare.originating_court is None and bare.originating_docket_number is None


def test_upsert_never_pulls_a_coa_docket_into_scope(tmp_path: Path) -> None:
    # The scope rule is the row's own court: ingesting a SCOTUS docket that links
    # back to a tracked ca9 docket leaves that CoA docket out of scope (it is
    # ingested for context and retrieval, never predicted).
    db = corpus.corpus_db_path(tmp_path)
    upsert_to_corpus(
        db, [from_bulk_row({"id": "55", "court_id": "ca9", "docket_number": "21-35466"})]
    )
    upsert_to_corpus(
        db,
        [
            from_api_docket(
                {
                    "id": 1,
                    "court_id": "scotus",
                    "appeal_from": "https://www.courtlistener.com/api/rest/v4/courts/ca9/",
                    "originating_court_information": {"docket_number": "21-35466"},
                }
            )
        ],
    )
    with corpus.connect(db) as conn:
        coa = corpus.get_row(conn, "ca9/55")
        scotus = corpus.get_row(conn, "scotus/1")
    assert coa is not None and coa.predict_eligible is False
    assert scotus is not None and scotus.predict_eligible is True
    # The link itself is still recorded — retrieval context, not scope.
    assert scotus.originating_docket_number == "21-35466"


def test_to_corpus_row_projects_onto_store_schema() -> None:
    store_row = to_corpus_row(from_api_docket(API_DOCKET))
    assert isinstance(store_row, corpus.CorpusRow)
    assert store_row.case_id == "ca9/64512345"
    assert store_row.case_name == "Doe v. Roe"  # the caption reaches the store
    assert store_row.topic == "Civil Rights"  # nature_of_suit -> topic
    assert store_row.judges == ["Alan Lee", "Jane Smith"]
    assert store_row.disposition == Disposition.granted_in_part
    # Enriched fields carry through to the storage row.
    assert store_row.parties == ["Jane Roe", "United States"]
    assert store_row.attorneys == ["A. Counsel"]
    assert store_row.precedential_status == "Published"
    assert store_row.citation_count == 5
    assert store_row.panel[0] == corpus.PanelMember(name="Jane Smith", seniority="active")


def test_bulk_circuit_rows_drop_the_cluster_joined_fields() -> None:
    """The bulk export's docket↔opinion-cluster join is misjoined on the circuit
    slices (19th-century cluster text on 2018-19 dockets), so the projection
    declines to store what the join cannot vouch for."""
    store_row = to_corpus_row(
        from_bulk_row({**BULK_ROW, "summary": "Per curiam.", "opinion_text": "The body."})
    )
    assert store_row.judges == []
    assert store_row.panel == []
    assert store_row.precedential_status is None
    assert store_row.summary is None
    assert store_row.citations == []
    assert store_row.citation_count is None
    # The body is withheld with the rest, so no non-SCOTUS row can carry one and
    # `has_opinion` never derives off a misjoined cluster's text.
    assert store_row.opinion_text is None
    assert store_row.has_opinion is False
    # Docket-side facts are unaffected: they come from the docket row itself.
    assert store_row.case_name == "Doe v. Roe"
    assert store_row.parties == ["Jane Roe", "United States"]
    assert store_row.disposition == Disposition.granted_in_part


def test_the_cluster_field_drop_is_bulk_circuit_only() -> None:
    # A bulk SCOTUS row keeps the cluster fields — the misjoin is observed only
    # on the circuit slices — and the REST path keeps them on every court (the
    # projection test above pins the api row).
    scotus = to_corpus_row(
        from_bulk_row({**BULK_ROW, "court_id": "scotus", "opinion_text": "The body."})
    )
    assert scotus.judges == ["Alan Lee", "Jane Smith"]
    assert scotus.precedential_status == "Published"
    assert scotus.citation_count == 5
    # A SCOTUS bulk row's body reaches the store, so the presence bit derives.
    assert scotus.opinion_text == "The body."
    assert scotus.has_opinion is True
    api = to_corpus_row(from_api_docket(API_DOCKET))
    assert api.judges == ["Alan Lee", "Jane Smith"]
    assert api.precedential_status == "Published"
    assert api.citation_count == 5


# Shared field names exempt from the pass-through guard below. Empty, and the
# guard is what keeps it empty: every exemption that would belong here is
# structurally impossible, because none of them shares a name across the two
# models. The storage row's caller-supplied channel state (`last_pulled`,
# `last_live_polled`, `sample_weight`) and its derived columns
# (`predict_eligible`, `has_opinion`) have no ingestion-model twin, and the one
# renamed field arrives under a different name (`nature_of_suit` -> `topic`).
# The cluster-join family the projection conditionally withholds is exempt only
# on a bulk circuit row; the guard feeds it a SCOTUS REST row, where those
# fields are expected to pass through like any other. So a field carrying the
# same name on both models is a straight-through field: add it to the
# projection rather than to this set.
_PROJECTION_EXEMPT: frozenset[str] = frozenset()


def _strip_optional(annotation: Any) -> Any:
    if get_origin(annotation) in (Union, UnionType):
        return next(a for a in get_args(annotation) if a is not type(None))
    return annotation


def _projection_sentinel(name: str, ordinal: int, *, parity: bool = False) -> Any:
    """A value unique to `name` where the type can carry one, typed as declared.

    Str/int/date/list sentinels are unique per field, so a projection that
    passes the *wrong* attribute into a column fails as loudly as one that
    drops it. Bools and enums cannot hold a per-field value in a single
    assignment, so the guard runs twice: an all-first-member pass (catching a
    dropped field — every storage default is falsy or None) and a `parity`
    pass varying the value by the field's index *within its own type group*
    (catching a swap between same-typed fields — ordinal parity would let two
    same-parity fields collide).
    """
    annotation = _strip_optional(IngestCorpusRow.model_fields[name].annotation)
    item = get_args(annotation)[0] if get_origin(annotation) is list else None
    value: Any
    if item is str:
        value = [f"{name}-sentinel"]
    elif item is corpus.PanelMember:
        value = [corpus.PanelMember(name=f"{name}-sentinel", seniority="active")]
    elif item is corpus.CounselEntry:
        value = [corpus.CounselEntry(party=f"{name}-sentinel")]
    elif annotation is bool:
        peers = sorted(
            n
            for n, f in IngestCorpusRow.model_fields.items()
            if _strip_optional(f.annotation) is bool
        )
        assert len(peers) <= 2, (
            "three bool fields cannot carry pairwise-distinct sentinels in two "
            "passes; extend the guard with a further assignment"
        )
        value = True if not parity else peers.index(name) == 0
    elif annotation is int:
        value = 7000 + ordinal
    elif annotation is str:
        value = f"{name}-sentinel"
    elif annotation is date:
        value = date(2031, 1, 1) + timedelta(days=ordinal)
    elif isinstance(annotation, type) and issubclass(annotation, Enum):
        members = list(annotation)
        peers = sorted(
            n
            for n, f in IngestCorpusRow.model_fields.items()
            if _strip_optional(f.annotation) is annotation
        )
        value = members[peers.index(name) % len(members)] if parity else members[0]
    else:
        raise AssertionError(
            f"no sentinel for {name}: {annotation}. A newly shared field needs one "
            "here so the projection guard can cover it."
        )
    return value


def test_every_shared_field_survives_the_projection() -> None:
    """Guard: a field carried by both models must actually cross the projection.

    `to_corpus_row` names its columns by hand, so a field added to both models
    and forgotten there is written as NULL by every ingestion path — silently,
    because nothing downstream distinguishes "never projected" from "upstream
    served nothing". This fills each shared field with a value unique to it and
    demands that same value back off the storage row, so the omission fails a
    test rather than reaching the corpus.
    """
    shared = (
        set(IngestCorpusRow.model_fields) & set(corpus.CorpusRow.model_fields)
    ) - _PROJECTION_EXEMPT
    for parity in (False, True):
        sentinels = {
            name: _projection_sentinel(name, i, parity=parity)
            for i, name in enumerate(sorted(shared))
        }
        # A SCOTUS REST row: neither condition under which the projection
        # withholds the cluster-join family (a bulk row, off a non-SCOTUS
        # court) holds, so every shared field is expected through.
        row = IngestCorpusRow(
            **{
                **sentinels,
                "case_id": "scotus/24100",
                "court": "scotus",
                "docket_id": 24100,
                "source": CorpusSource.api,
            }
        )
        store_row = to_corpus_row(row)
        lost = {
            name: (getattr(row, name), getattr(store_row, name))
            for name in sorted(shared)
            if getattr(store_row, name) != getattr(row, name)
        }
        assert not lost, f"shared fields lost in to_corpus_row (ingested, stored): {lost}"


def test_the_response_and_merits_brief_dates_reach_the_store() -> None:
    """The dated siblings of the interim escalation flags are docket facts.

    `response_requested` without `response_requested_at` is the flag asserting
    the Court asked while the row cannot say when, which is the shape an
    undated request legitimately takes — so a projection that drops the date
    makes every request look undated. Built through the shared normalizer
    (`from_api_docket`); in production only the live channel mints these three.
    The introspection guard above covers the channel-independent projection —
    this pins the three names so the regression reads as itself.
    """
    row = from_api_docket(
        {
            **API_DOCKET,
            "court": "https://www.courtlistener.com/api/rest/v4/courts/scotus/",
            "response_requested": True,
            "response_requested_at": "2026-03-02",
            "response_filed_at": "2026-03-20",
            "merits_brief_filed": "2026-05-11",
        }
    )
    store_row = to_corpus_row(row)
    assert store_row.response_requested is True
    assert store_row.response_requested_at == date(2026, 3, 2)
    assert store_row.response_filed_at == date(2026, 3, 20)
    assert store_row.merits_brief_filed == date(2026, 5, 11)


def test_a_summary_and_an_opinion_body_are_separate_columns() -> None:
    """A short retrieval blurb and the decision's full text are different facts.

    Folding a body into `summary` would leave `has_opinion` — the presence bit
    every opinion-coverage reader ORs on — underivable from the row.
    """
    both = from_api_docket({**API_DOCKET, "summary": "Per curiam.", "opinion_text": "The body."})
    assert both.summary == "Per curiam."
    assert both.opinion_text == "The body."
    # Each stands alone: a source serving only one fills only that column.
    body_only = from_api_docket({**API_DOCKET, "opinion_text": "The body."})
    assert body_only.summary is None and body_only.opinion_text == "The body."
    summary_only = from_api_docket({**API_DOCKET, "summary": "Per curiam."})
    assert summary_only.summary == "Per curiam." and summary_only.opinion_text is None


def test_a_reserved_bulk_row_clears_a_stored_misjoin(tmp_path: Path) -> None:
    """``summary`` / ``precedential_status`` / ``judges`` take the incoming value
    on upsert (no latch), so re-serving the bulk slice heals rows the misjoined
    import wrote rather than leaving the garbage latched."""
    db = corpus.corpus_db_path(tmp_path)
    upsert_to_corpus(db, [from_api_docket(API_DOCKET)])  # a row with the fields set
    upsert_to_corpus(db, [from_bulk_row(BULK_ROW)])  # the same case, re-served by bulk
    with corpus.connect(db) as conn:
        fetched = corpus.get_row(conn, "ca9/64512345")
    assert fetched is not None
    assert fetched.summary is None
    assert fetched.precedential_status is None
    assert fetched.judges == []
    assert fetched.panel == []
    assert fetched.citations == []
    assert fetched.citation_count is None


def test_enriched_fields_round_trip_through_the_corpus(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path)
    upsert_to_corpus(db, [from_api_docket(API_DOCKET)])
    with corpus.connect(db) as conn:
        fetched = corpus.get_row(conn, "ca9/64512345")
    assert fetched is not None
    assert fetched.parties == ["Jane Roe", "United States"]
    assert fetched.attorneys == ["A. Counsel"]
    assert fetched.precedential_status == "Published"
    assert fetched.citation_count == 5
    assert fetched.panel == [
        corpus.PanelMember(name="Jane Smith", seniority="active"),
        corpus.PanelMember(name="Alan Lee", seniority="senior"),
    ]


def test_upsert_to_corpus_persists_rows(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path)
    rows = [from_api_docket(API_DOCKET), from_bulk_row({"id": "9", "court_id": "ca1"})]
    assert upsert_to_corpus(db, rows) == 2
    with corpus.connect(db) as conn:
        assert {r.case_id for r in corpus.iter_rows(conn)} == {"ca9/64512345", "ca1/9"}


def test_default_event_for_appeal() -> None:
    event = default_event(from_api_docket(API_DOCKET))
    assert event.case_id == "ca9/64512345"
    assert event.court == "ca9"
    assert event.kind == EventKind.appeal
    assert event.event_id == "evt-appeal-disposition"
    assert event.stage is None  # a circuit appeal has no SCOTUS decision standard
    assert event.title == "Doe v. Roe"
    assert event.opened_at == date(2021, 3, 1)
    # API_DOCKET carries a disposition, so the event is already resolved.
    assert event.resolved is True


def test_default_event_for_scotus_is_a_petition() -> None:
    event = default_event(from_bulk_row({"id": "5", "court_id": "scotus"}))
    assert event.kind == EventKind.petition
    assert event.event_id == "evt-petition-disposition"
    assert event.stage == "cert"
    assert event.resolved is False  # no disposition yet
    assert event.title == "scotus/5"  # falls back to case_id when unnamed


def test_default_event_for_scotus_application_is_a_motion() -> None:
    # A `YYAnnn` application docket is a stay/injunction application — a motion
    # under the interim standard, not a cert petition. Keyed on the docket
    # number's form alone, so it holds even before the live channel's
    # `application_kind` parse has run.
    event = default_event(
        from_bulk_row({"id": "6", "court_id": "scotus", "docket_number": "24A1099"})
    )
    assert event.kind == EventKind.motion
    assert event.event_id == "evt-motion-disposition"
    assert event.stage == "interim"
    assert event.decision_target == "disposition"


def test_default_event_application_form_outside_scotus_is_still_an_appeal() -> None:
    # The application-number key is SCOTUS-only; a circuit docket that happens
    # to parse as `YYAnnn` keeps the appeal baseline.
    event = default_event(from_bulk_row({"id": "7", "court_id": "ca9", "docket_number": "24A109"}))
    assert event.kind == EventKind.appeal
    assert event.event_id == "evt-appeal-disposition"
    assert event.stage is None


def test_upsert_to_corpus_is_idempotent_by_case(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path)
    upsert_to_corpus(db, [from_bulk_row({**BULK_ROW, "nature_of_suit": "old"})])
    upsert_to_corpus(db, [from_api_docket(API_DOCKET)])  # same case_id, fresher facts
    with corpus.connect(db) as conn:
        assert corpus.count(conn) == 1
        fetched = corpus.get_row(conn, "ca9/64512345")
    assert fetched is not None
    assert fetched.topic == "Civil Rights"
