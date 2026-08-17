"""The staging-corpus seeder (``fedcourtsai.corpus_seed``), fully offline.

Both destinations are in-memory transports injected through the seams the
corpus transports already expose — no boto3, no network — mirroring
``test_corpus_remote.py`` and ``test_casestore.py``.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import casestore, corpus, corpus_ranged, corpus_seed
from fedcourtsai.cli import app
from fedcourtsai.config import Settings

from .test_corpus_remote import InMemoryFileTransport

runner = CliRunner()

PROD_REMOTE = "s3://fcai-prod/corpus"
PROD_CASESTORE = "s3://fcai-prod/casestore/v1"
STAGING_REMOTE = "s3://fcai-staging/corpus"
STAGING_CASESTORE = "s3://fcai-staging/casestore/v1"

# Two SCOTUS petitions and one circuit docket: enough to prove the slice is a
# selection rather than a copy, and that a non-slice case never travels.
SLICE_CASES = ("scotus/74112233", "scotus/74112234")
OTHER_CASE = "ca9/64512345"


def _settings() -> Settings:
    """Settings naming the production stores — what the safety rail compares to."""
    return Settings(corpus_remote_url=PROD_REMOTE, casestore_url=PROD_CASESTORE)


def _row(case_id: str, **kwargs: object) -> corpus.CorpusRow:
    court = case_id.split("/", 1)[0]
    return corpus.CorpusRow(case_id=case_id, court=court, docket_number="25-9", **kwargs)


def _event(case_id: str, event_id: str = "evt-petition-disposition") -> corpus.CorpusEvent:
    return corpus.CorpusEvent(
        event_id=event_id,
        case_id=case_id,
        court=case_id.split("/", 1)[0],
        kind="petition" if case_id.startswith("scotus/") else "appeal",
        title="A v. B",
    )


@pytest.fixture
def source_db(tmp_path: Path) -> Path:
    """A miniature production corpus: three cases, one carrying an opinion body."""
    db = tmp_path / "source" / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                _row(SLICE_CASES[0], opinion_text="The judgment below is reversed."),
                _row(SLICE_CASES[1]),
                _row(OTHER_CASE),
            ],
        )
        corpus.upsert_events(
            conn,
            [
                _event(SLICE_CASES[0]),
                _event(SLICE_CASES[0], "evt-order-judgment"),
                _event(SLICE_CASES[1]),
                _event(OTHER_CASE),
            ],
        )
    return db


@pytest.fixture
def source_objects() -> casestore.InMemoryObjectTransport:
    """A miniature production content store: snapshots, documents, manifests."""
    transport = casestore.InMemoryObjectTransport()
    for case_id in (*SLICE_CASES, OTHER_CASE):
        casestore.write_case(transport, _row(case_id))
        casestore.write_events(transport, case_id, [_event(case_id)])
        casestore.write_snapshot(transport, case_id, date(2026, 6, 1), {"id": 1})
        casestore.write_snapshot(transport, case_id, date(2026, 7, 1), {"id": 2})
        casestore.write_documents(
            transport,
            case_id,
            [
                corpus.CaseDocument(
                    case_id=case_id,
                    kind="petition",
                    url="https://sc.gov/petition.pdf",
                    fetched_at=date(2026, 6, 1),
                    text=f"petition text for {case_id}",
                )
            ],
        )
    return transport


def _seed(
    source_db: Path,
    source_objects: casestore.InMemoryObjectTransport,
    tmp_path: Path,
    *,
    dest_objects: casestore.InMemoryObjectTransport,
    blob_transport: InMemoryFileTransport,
    case_ids: tuple[str, ...] = SLICE_CASES,
    apply: bool = False,
    max_cases: int = corpus_seed.DEFAULT_MAX_CASES,
) -> corpus_seed.SeedResult:
    with corpus.connect(source_db) as conn:
        return corpus_seed.seed_slice(
            source_conn=conn,
            case_ids=case_ids,
            destination=corpus_seed.Destination(
                remote_url=STAGING_REMOTE,
                casestore_url=STAGING_CASESTORE,
                objects=dest_objects,
                blob_transport=blob_transport,
            ),
            settings=_settings(),
            stage_db=tmp_path / "stage" / "staging-slice.db",
            source_objects=source_objects,
            apply=apply,
            max_cases=max_cases,
        )


# --- the requested slice ------------------------------------------------------


def test_case_ids_come_from_options_and_a_file(tmp_path: Path) -> None:
    listing = tmp_path / "dockets.txt"
    listing.write_text(
        "# the staging slice\n"
        + "scotus/74112234\n"
        + "\n"
        + "scotus/74112235  # a relisted petition\n"
    )
    assert corpus_seed.parse_case_ids(["scotus/74112233"], path=listing) == [
        "scotus/74112233",
        "scotus/74112234",
        "scotus/74112235",
    ]


def test_case_ids_are_deduplicated_in_request_order() -> None:
    values = ["scotus/74112234", "scotus/74112233", "scotus/74112234"]
    assert corpus_seed.parse_case_ids(values) == ["scotus/74112234", "scotus/74112233"]


@pytest.mark.parametrize("bad", ["scotus", "SCOTUS/74112233", "scotus/abc", "../etc"])
def test_a_malformed_case_id_is_refused(bad: str) -> None:
    with pytest.raises(corpus_seed.SeedSliceError, match="case id"):
        corpus_seed.parse_case_ids([bad])


def test_an_empty_slice_is_refused() -> None:
    with pytest.raises(corpus_seed.SeedSliceError, match="names no case"):
        corpus_seed.parse_case_ids(["  ", "# nothing here"])


# --- the safety rail ----------------------------------------------------------


@pytest.mark.parametrize(
    ("dest_remote", "dest_casestore"),
    [
        (PROD_REMOTE, STAGING_CASESTORE),
        (STAGING_REMOTE, PROD_CASESTORE),
        # Case and a trailing slash must not defeat the comparison.
        (PROD_REMOTE.upper() + "/", STAGING_CASESTORE),
        # A destination that names the *other* production store is just as wrong.
        (PROD_CASESTORE, STAGING_CASESTORE),
    ],
)
def test_a_production_destination_is_refused(dest_remote: str, dest_casestore: str) -> None:
    with pytest.raises(corpus_seed.SeedSliceError, match="refusing to seed"):
        corpus_seed.assert_destination_is_not_production(
            corpus_seed.Destination(remote_url=dest_remote, casestore_url=dest_casestore),
            settings=_settings(),
        )


def test_the_rail_refuses_before_anything_is_read(
    source_db: Path,
    source_objects: casestore.InMemoryObjectTransport,
    tmp_path: Path,
) -> None:
    dest_objects = casestore.InMemoryObjectTransport()
    blob_transport = InMemoryFileTransport()
    with corpus.connect(source_db) as conn, pytest.raises(corpus_seed.SeedSliceError):
        corpus_seed.seed_slice(
            source_conn=conn,
            case_ids=SLICE_CASES,
            destination=corpus_seed.Destination(
                remote_url=PROD_REMOTE,
                casestore_url=PROD_CASESTORE,
                objects=dest_objects,
                blob_transport=blob_transport,
            ),
            settings=_settings(),
            stage_db=tmp_path / "stage" / "staging-slice.db",
            source_objects=source_objects,
            apply=True,
        )
    assert dest_objects.objects == {}
    assert blob_transport.objects == {}


def test_a_malformed_destination_url_is_refused() -> None:
    with pytest.raises(corpus_ranged.RangedBackendError):
        corpus_seed.assert_destination_is_not_production(
            corpus_seed.Destination(
                remote_url="https://example.invalid/corpus",
                casestore_url=STAGING_CASESTORE,
            ),
            settings=_settings(),
        )


# --- the dry-run census -------------------------------------------------------


def test_dry_run_counts_the_slice_and_writes_nothing(
    source_db: Path,
    source_objects: casestore.InMemoryObjectTransport,
    tmp_path: Path,
) -> None:
    dest_objects = casestore.InMemoryObjectTransport()
    blob_transport = InMemoryFileTransport()

    result = _seed(
        source_db,
        source_objects,
        tmp_path,
        dest_objects=dest_objects,
        blob_transport=blob_transport,
    )

    assert not result.applied
    assert [case.case_id for case in result.census.cases] == list(SLICE_CASES)
    assert result.census.rows == 2
    # Two events on the first case, one on the second.
    assert result.census.events == 3
    for case in result.census.cases:
        assert case.present
        assert case.snapshots == 2
        # One content-addressed document leaf; the manifest is not a document.
        assert case.documents == 1
        # case.json + events.json + 2 snapshots + 1 leaf + the manifest.
        assert case.objects == 6
    assert result.census.objects == 12
    # Nothing was written on either half.
    assert dest_objects.objects == {}
    assert blob_transport.objects == {}
    assert not (tmp_path / "stage" / "staging-slice.db").exists()


def test_a_requested_case_the_corpus_lacks_is_reported_not_fatal(
    source_db: Path,
    source_objects: casestore.InMemoryObjectTransport,
    tmp_path: Path,
) -> None:
    result = _seed(
        source_db,
        source_objects,
        tmp_path,
        dest_objects=casestore.InMemoryObjectTransport(),
        blob_transport=InMemoryFileTransport(),
        case_ids=(SLICE_CASES[0], "scotus/99999999"),
    )
    assert result.census.missing == ("scotus/99999999",)
    assert result.census.rows == 1


# --- the bound ----------------------------------------------------------------


def test_max_cases_bounds_the_slice_and_reports_the_drop(
    source_db: Path,
    source_objects: casestore.InMemoryObjectTransport,
    tmp_path: Path,
) -> None:
    dest_objects = casestore.InMemoryObjectTransport()

    result = _seed(
        source_db,
        source_objects,
        tmp_path,
        dest_objects=dest_objects,
        blob_transport=InMemoryFileTransport(),
        case_ids=(*SLICE_CASES, OTHER_CASE),
        apply=True,
        max_cases=1,
    )

    assert result.census.requested == 3
    assert result.census.dropped == 2
    assert [case.case_id for case in result.census.cases] == [SLICE_CASES[0]]
    assert result.rows == 1
    # Only the bounded case's objects travelled.
    assert all(key.startswith(f"{SLICE_CASES[0]}/") for key in dest_objects.objects)


def test_a_zero_bound_is_refused() -> None:
    with pytest.raises(corpus_seed.SeedSliceError, match="at least 1"):
        corpus_seed.bound_cases(list(SLICE_CASES), 0)


# --- the apply ----------------------------------------------------------------


def test_apply_seeds_rows_events_and_objects(
    source_db: Path,
    source_objects: casestore.InMemoryObjectTransport,
    tmp_path: Path,
) -> None:
    dest_objects = casestore.InMemoryObjectTransport()
    blob_transport = InMemoryFileTransport()

    result = _seed(
        source_db,
        source_objects,
        tmp_path,
        dest_objects=dest_objects,
        blob_transport=blob_transport,
        apply=True,
    )

    assert result.applied
    assert (result.rows, result.events) == (2, 3)
    assert result.objects_copied == 12
    assert result.objects_present == 0

    # The blob half: only the slice's rows and events, opinion body stripped,
    # and no payload rows at all — split-on parity whatever the seeding mode.
    stage = tmp_path / "stage" / "staging-slice.db"
    with corpus.connect(stage) as conn:
        assert {row.case_id for row in corpus.iter_rows(conn)} == set(SLICE_CASES)
        seeded = corpus.get_row(conn, SLICE_CASES[0])
        assert seeded is not None
        assert seeded.opinion_text is None
        # The retained presence bit still says a body exists upstream.
        assert seeded.has_opinion
        assert len(corpus.events_for_case(conn, SLICE_CASES[0])) == 2
        assert conn.execute("SELECT COUNT(*) FROM snapshots").fetchone()[0] == 0
        assert conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0] == 0

    # The store half: a byte-for-byte copy of the slice's objects, and nothing
    # belonging to a case outside it.
    assert not any(key.startswith(f"{OTHER_CASE}/") for key in dest_objects.objects)
    for key, body in dest_objects.objects.items():
        assert body == source_objects.objects[key]

    # The pointer names the published blob, content-addressed like production's.
    assert result.pointer is not None
    assert result.pointer.key == f"index/sha256/{result.pointer.sha256}"
    assert blob_transport.objects[f"corpus/{result.pointer.key}"] == stage.read_bytes()
    # And it round-trips through the ranged resolver, as a real pointer must.
    written = corpus_ranged.read_index_pointer(stage.with_name(stage.name + ".ref"))
    assert written == result.pointer


def test_the_seeded_blob_satisfies_the_ranged_read_layout(
    source_db: Path,
    source_objects: casestore.InMemoryObjectTransport,
    tmp_path: Path,
) -> None:
    _seed(
        source_db,
        source_objects,
        tmp_path,
        dest_objects=casestore.InMemoryObjectTransport(),
        blob_transport=InMemoryFileTransport(),
        apply=True,
    )
    assert corpus.check_ranged_layout(tmp_path / "stage" / "staging-slice.db") == []


def test_a_second_apply_converges(
    source_db: Path,
    source_objects: casestore.InMemoryObjectTransport,
    tmp_path: Path,
) -> None:
    dest_objects = casestore.InMemoryObjectTransport()
    blob_transport = InMemoryFileTransport()
    first = _seed(
        source_db,
        source_objects,
        tmp_path,
        dest_objects=dest_objects,
        blob_transport=blob_transport,
        apply=True,
    )
    objects_after_first = dict(dest_objects.objects)

    second = _seed(
        source_db,
        source_objects,
        tmp_path,
        dest_objects=dest_objects,
        blob_transport=blob_transport,
        apply=True,
    )

    # Every object was already present, so nothing was re-copied…
    assert second.objects_copied == 0
    assert second.objects_present == first.objects_copied
    assert dest_objects.objects == objects_after_first
    # …and the content-addressed blob key is unchanged, so no re-upload either.
    assert second.pointer == first.pointer
    assert blob_transport.uploads == 1


def test_the_production_content_store_is_never_mirrored_to(
    source_db: Path,
    source_objects: casestore.InMemoryObjectTransport,
    tmp_path: Path,
) -> None:
    """The corpus write seams dual-write to the *process* store; a seed must not.

    Standing the production store up as the process transport is exactly the
    accident the build guards against, so assert on that arrangement directly.
    """
    casestore.set_active_transport(source_objects)
    before = dict(source_objects.objects)
    try:
        _seed(
            source_db,
            source_objects,
            tmp_path,
            dest_objects=casestore.InMemoryObjectTransport(),
            blob_transport=InMemoryFileTransport(),
            apply=True,
        )
    finally:
        casestore.reset_active_transport()
    assert source_objects.objects == before


# --- the rendering ------------------------------------------------------------


def test_the_summary_renders_the_census_and_the_published_pointer(
    source_db: Path,
    source_objects: casestore.InMemoryObjectTransport,
    tmp_path: Path,
) -> None:
    result = _seed(
        source_db,
        source_objects,
        tmp_path,
        dest_objects=casestore.InMemoryObjectTransport(),
        blob_transport=InMemoryFileTransport(),
        apply=True,
    )
    markdown = result.render_markdown()
    assert "Staging corpus slice (applied)" in markdown
    for case_id in SLICE_CASES:
        assert f"`{case_id}`" in markdown
    assert result.pointer is not None
    assert result.pointer.sha256 in markdown

    dry = _seed(
        source_db,
        source_objects,
        tmp_path,
        dest_objects=casestore.InMemoryObjectTransport(),
        blob_transport=InMemoryFileTransport(),
    ).render_markdown()
    assert "Staging corpus slice (dry run)" in dry
    assert "nothing written" in dry


# --- the command --------------------------------------------------------------


def _prod_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("FEDCOURTS_CORPUS_REMOTE_URL", PROD_REMOTE)
    monkeypatch.setenv("FEDCOURTS_CASESTORE_URL", PROD_CASESTORE)
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))


def test_the_command_refuses_a_production_destination(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _prod_env(monkeypatch, tmp_path)
    result = runner.invoke(
        app,
        [
            "corpus-seed-slice",
            "--dest-remote",
            PROD_REMOTE,
            "--dest-casestore",
            STAGING_CASESTORE,
            "--dockets",
            SLICE_CASES[0],
            "--apply",
        ],
    )
    assert result.exit_code == 2
    assert "refusing to seed" in result.output


def test_the_command_needs_a_source_content_store(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _prod_env(monkeypatch, tmp_path)
    monkeypatch.setenv("FEDCOURTS_CASESTORE_URL", "")
    result = runner.invoke(
        app,
        [
            "corpus-seed-slice",
            "--dest-remote",
            STAGING_REMOTE,
            "--dest-casestore",
            STAGING_CASESTORE,
            "--dockets",
            SLICE_CASES[0],
        ],
    )
    assert result.exit_code == 1
    assert "source content store is not configured" in result.output


def test_the_command_says_so_when_the_corpus_is_not_pulled(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _prod_env(monkeypatch, tmp_path)
    result = runner.invoke(
        app,
        [
            "corpus-seed-slice",
            "--dest-remote",
            STAGING_REMOTE,
            "--dest-casestore",
            STAGING_CASESTORE,
            "--dockets",
            SLICE_CASES[0],
        ],
    )
    assert result.exit_code == 1
    assert "no corpus at" in result.output


def test_the_command_refuses_a_malformed_case_id(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _prod_env(monkeypatch, tmp_path)
    result = runner.invoke(
        app,
        [
            "corpus-seed-slice",
            "--dest-remote",
            STAGING_REMOTE,
            "--dest-casestore",
            STAGING_CASESTORE,
            "--dockets",
            "not-a-case-id",
        ],
    )
    assert result.exit_code == 2
    assert "case id" in result.output
