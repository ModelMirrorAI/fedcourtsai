"""The staging corpus slice seeder (``fedcourtsai.corpus_seed``), fully offline.

Both destinations are in-memory transports injected through the seams the
corpus transports already expose — no boto3, no network — mirroring
``test_corpus_remote.py`` and ``test_casestore.py``.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import casestore, corpus, corpus_ranged, corpus_remote, corpus_seed
from fedcourtsai.cli import app
from fedcourtsai.config import Settings

from .test_corpus_remote import InMemoryFileTransport

runner = CliRunner()

PROD_BUCKET = "fcai-prod"
PROD_REMOTE = f"s3://{PROD_BUCKET}/corpus"
# The bare-bucket spelling of the production content store: `parse_s3_url`
# yields no prefix and the transport falls back to DEFAULT_PREFIX, which is
# exactly the configured URL below.
PROD_CASESTORE = f"s3://{PROD_BUCKET}/{casestore.DEFAULT_PREFIX}"
STAGING_REMOTE = "s3://fcai-staging/corpus"
STAGING_CASESTORE = "s3://fcai-staging/casestore/v1"

# Two SCOTUS petitions and one circuit docket: enough to prove the slice is a
# selection rather than a copy, and that a non-slice case never travels.
SLICE_CASES = ("scotus/74112233", "scotus/74112234")
OTHER_CASE = "ca9/64512345"


def _settings() -> Settings:
    """Settings naming the production stores — the ambient environment, which
    the rail deliberately does NOT compare against."""
    return Settings(corpus_remote_url=PROD_REMOTE, casestore_url=PROD_CASESTORE)


def _flipped_settings() -> Settings:
    """The post-repoint environment: ambient variables naming the staging pair."""
    return Settings(corpus_remote_url=STAGING_REMOTE, casestore_url=STAGING_CASESTORE)


def _source() -> corpus_seed.Source:
    """The pinned source — the production pair, as the workflow pins it."""
    return corpus_seed.Source(remote_url=PROD_REMOTE, casestore_url=PROD_CASESTORE)


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
            source=corpus_seed.Source(
                remote_url=PROD_REMOTE,
                casestore_url=PROD_CASESTORE,
                objects=source_objects,
            ),
            case_ids=case_ids,
            destination=corpus_seed.Destination(
                remote_url=STAGING_REMOTE,
                casestore_url=STAGING_CASESTORE,
                objects=dest_objects,
                blob_transport=blob_transport,
            ),
            settings=_settings(),
            stage_db=tmp_path / "stage" / "staging-slice.db",
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


# Each case pins the DISTINGUISHING message, not just "refusing to seed": the
# rail has two branches — an exact-location match and the coarser
# bucket-disjointness rule — and a test that accepted either would pass with
# the exact-location branch deleted, since the bucket check subsumes every case
# it catches.
_EXACT = "names the pinned source"
_INSIDE = "is a prefix inside the pinned source"


@pytest.mark.parametrize(
    ("dest_remote", "dest_casestore", "expected"),
    [
        (PROD_REMOTE, STAGING_CASESTORE, _EXACT),
        (STAGING_REMOTE, PROD_CASESTORE, _EXACT),
        # Bucket/prefix case and a trailing slash must not defeat the exact
        # comparison. (An upper-cased *scheme* is refused a step earlier, as
        # malformed — the transports' parsers do not accept one either.)
        (f"s3://{PROD_BUCKET.upper()}/CORPUS/", STAGING_CASESTORE, _EXACT),
        # A destination naming the *other* production store — the slots are
        # not checked against their own counterpart only, so this is still an
        # exact match and is diagnosed as one.
        (PROD_CASESTORE, STAGING_CASESTORE, _EXACT),
        # A BARE production bucket in the content-store slot: the transport
        # falls back to DEFAULT_PREFIX, so this resolves to exactly the
        # production store even though the URL string differs.
        (STAGING_REMOTE, f"s3://{PROD_BUCKET}", _EXACT),
        # A doubled slash: same location, different spelling — still exact.
        (f"s3://{PROD_BUCKET}//corpus", STAGING_CASESTORE, _EXACT),
        # Prefixes *inside* the production bucket — the runbook's own
        # separate-bucket invariant, enforced rather than merely stated.
        (f"s3://{PROD_BUCKET}/corpus/staging-slice", STAGING_CASESTORE, _INSIDE),
        (STAGING_REMOTE, f"s3://{PROD_BUCKET}/somewhere/else", _INSIDE),
    ],
)
def test_a_destination_that_is_the_source_is_refused(
    dest_remote: str, dest_casestore: str, expected: str
) -> None:
    with pytest.raises(corpus_seed.SeedSliceError) as caught:
        corpus_seed.assert_destination_is_not_the_source(
            corpus_seed.Destination(remote_url=dest_remote, casestore_url=dest_casestore),
            source=_source(),
        )
    assert "refusing to seed" in str(caught.value)
    assert expected in str(caught.value)


def test_a_staging_destination_is_allowed() -> None:
    """The rail must not be so coarse that it refuses the intended pair."""
    corpus_seed.assert_destination_is_not_the_source(
        corpus_seed.Destination(remote_url=STAGING_REMOTE, casestore_url=STAGING_CASESTORE),
        source=_source(),
    )


def test_the_rail_follows_the_pin_not_the_environment() -> None:
    """The rail's basis is the pinned source, never the ambient settings.

    The staging runbook repoints the environment's corpus variables at the
    staging pair. A rail based on those variables would then read the staging
    destination as "production" and refuse every legitimate re-seed — while a
    seeder sourcing from them would read the staging pair as its own source.
    So: with the environment flipped and the pin on production, the staging
    destination is allowed; with the pin itself naming the staging pair, the
    same destination is refused as a self-seed, whatever the environment says.
    """
    staging_destination = corpus_seed.Destination(
        remote_url=STAGING_REMOTE, casestore_url=STAGING_CASESTORE
    )
    # The flipped environment is not consulted: only the pin decides.
    corpus_seed.assert_destination_is_not_the_source(staging_destination, source=_source())
    with pytest.raises(corpus_seed.SeedSliceError, match="names the pinned source"):
        corpus_seed.assert_destination_is_not_the_source(
            staging_destination,
            source=corpus_seed.Source(remote_url=STAGING_REMOTE, casestore_url=STAGING_CASESTORE),
        )


@pytest.mark.parametrize("blank", ["", "   "])
@pytest.mark.parametrize("slot", ["remote_url", "casestore_url"])
def test_an_unpinned_source_url_fails_closed(slot: str, blank: str) -> None:
    """Half a comparison basis is no basis: an empty pin refuses to construct."""
    urls = {"remote_url": PROD_REMOTE, "casestore_url": PROD_CASESTORE, slot: blank}
    with pytest.raises(corpus_seed.SeedSliceError, match="not pinned"):
        corpus_seed.Source(**urls)


def test_a_pointer_override_is_refused() -> None:
    """The index half of the self-seeding hazard: no seed under an override."""
    pointer = json.dumps(
        {"key": "corpus/db/sha256/aa.db", "schema_version": "1", "sha256": "aa", "size": 1}
    )
    with pytest.raises(corpus_seed.SeedSliceError, match="pointer override"):
        corpus_seed.assert_no_pointer_override(
            _settings().model_copy(update={"corpus_pointer": pointer})
        )
    # Unset — and the empty spelling the settings validator maps to unset —
    # both pass: only a live override is the hazard.
    corpus_seed.assert_no_pointer_override(_settings())
    corpus_seed.assert_no_pointer_override(Settings(corpus_pointer=""))


def test_a_malformed_source_url_is_refused() -> None:
    bad = "https://example.invalid/corpus"
    with pytest.raises(corpus_seed.SeedSliceError) as caught:
        corpus_seed.assert_destination_is_not_the_source(
            corpus_seed.Destination(remote_url=STAGING_REMOTE, casestore_url=STAGING_CASESTORE),
            source=corpus_seed.Source(remote_url=bad, casestore_url=PROD_CASESTORE),
        )
    # Names the slot, never the URL — same discipline as the destination's.
    assert "--source-remote" in str(caught.value)
    assert bad not in str(caught.value)


def test_a_stage_db_on_the_committed_corpus_is_refused(tmp_path: Path) -> None:
    """`upload_index` writes the pointer beside the blob — never onto production's."""
    settings = _settings().model_copy(update={"corpus_root": tmp_path / "corpus"})
    with pytest.raises(corpus_seed.SeedSliceError, match="--stage-db is the corpus blob"):
        corpus_seed.assert_stage_db_is_not_the_corpus(
            tmp_path / "corpus" / "corpus.db", settings=settings
        )
    # An unresolved spelling of the same file is the same file.
    with pytest.raises(corpus_seed.SeedSliceError, match="--stage-db is the corpus blob"):
        corpus_seed.assert_stage_db_is_not_the_corpus(
            tmp_path / "corpus" / "." / "corpus.db", settings=settings
        )
    # The default working file sits beside it and is fine.
    corpus_seed.assert_stage_db_is_not_the_corpus(
        tmp_path / "corpus" / "staging-slice.db", settings=settings
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
            source=corpus_seed.Source(
                remote_url=PROD_REMOTE,
                casestore_url=PROD_CASESTORE,
                objects=source_objects,
            ),
            case_ids=SLICE_CASES,
            destination=corpus_seed.Destination(
                remote_url=PROD_REMOTE,
                casestore_url=PROD_CASESTORE,
                objects=dest_objects,
                blob_transport=blob_transport,
            ),
            settings=_settings(),
            stage_db=tmp_path / "stage" / "staging-slice.db",
            apply=True,
        )
    assert dest_objects.objects == {}
    assert blob_transport.objects == {}


def test_a_malformed_destination_url_is_refused() -> None:
    bad = "https://example.invalid/corpus"
    with pytest.raises(corpus_seed.SeedSliceError) as caught:
        corpus_seed.assert_destination_is_not_the_source(
            corpus_seed.Destination(remote_url=bad, casestore_url=STAGING_CASESTORE),
            source=_source(),
        )
    # Names the slot, never the URL: a rail message reaches run logs and a PR,
    # and a store URL is supplied out of band and never published.
    assert "--dest-remote" in str(caught.value)
    assert bad not in str(caught.value)


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
    assert result.objects.copied == 12
    assert (result.objects.skipped, result.objects.unreadable) == (0, 0)

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

    # The write-once keys were already present, so only the three mutable
    # manifests per case were re-copied — and the bytes are identical, so the
    # destination is unchanged either way.
    mutable_per_case = len(corpus_seed._MUTABLE_KEYS)
    assert second.objects.copied == mutable_per_case * len(SLICE_CASES)
    assert second.objects.skipped == first.objects.copied - second.objects.copied
    assert second.objects.unreadable == 0
    assert dest_objects.objects == objects_after_first
    # …and the content-addressed blob key is unchanged, so no re-upload either.
    assert second.pointer == first.pointer
    assert blob_transport.uploads == 1


def test_a_re_seed_refreshes_the_mutable_manifests(
    source_db: Path,
    source_objects: casestore.InMemoryObjectTransport,
    tmp_path: Path,
) -> None:
    """The three overwrite-in-place keys must track the source, or the two halves
    of the staging corpus describe different cases.

    Skipping them on the second apply leaves a manifest naming a superseded
    petition (with the new leaf sitting unreachable beside it) and a `case.json`
    still saying the case is undecided — while the blob half, rebuilt from
    scratch every apply, says denied.
    """
    dest_objects = casestore.InMemoryObjectTransport()
    blob_transport = InMemoryFileTransport()
    case_id = SLICE_CASES[0]
    _seed(
        source_db,
        source_objects,
        tmp_path,
        dest_objects=dest_objects,
        blob_transport=blob_transport,
        apply=True,
    )

    # The case moves on at the source, exactly as a re-ingest would move it: a
    # superseding petition (a NEW content-addressed leaf plus a rewritten
    # manifest), a rewritten case.json, and a rewritten events.json.
    superseded = corpus.CaseDocument(
        case_id=case_id,
        kind="petition",
        url="https://sc.gov/petition-v2.pdf",
        fetched_at=date(2026, 8, 1),
        text=f"superseding petition text for {case_id}",
    )
    casestore.merge_documents(source_objects, case_id, [superseded])
    casestore.write_case(source_objects, _row(case_id, disposition="denied"))
    casestore.write_events(
        source_objects, case_id, [_event(case_id), _event(case_id, "evt-order-judgment")]
    )
    with corpus.connect(source_db) as conn:
        corpus.upsert_rows(conn, [_row(case_id, disposition="denied")])

    second = _seed(
        source_db,
        source_objects,
        tmp_path,
        dest_objects=dest_objects,
        blob_transport=blob_transport,
        apply=True,
    )

    # Every mutable key tracked the source, byte for byte.
    for mutable in corpus_seed._MUTABLE_KEYS:
        key = f"{case_id}/{mutable}"
        assert dest_objects.objects[key] == source_objects.objects[key], key
    # The manifest names the new leaf, and that leaf is actually present.
    manifest = json.loads(dest_objects.objects[f"{case_id}/documents/documents.json"])
    text_key = manifest["documents"][0]["text_key"]
    assert "petition-v2" not in text_key  # keys are content-addressed, not named
    assert dest_objects.objects[text_key].decode() == superseded.text
    # And case.json agrees with the blob half about the disposition.
    assert json.loads(dest_objects.objects[f"{case_id}/case.json"])["disposition"] == "denied"
    with corpus.connect(tmp_path / "stage" / "staging-slice.db") as conn:
        seeded = corpus.get_row(conn, case_id)
        assert seeded is not None
        assert seeded.disposition == "denied"
    # The new leaf is a new key, so it counts as a copy on top of the mutables.
    assert second.objects.copied == corpus_seed._MUTABLE_KEYS.__len__() * len(SLICE_CASES) + 1


def test_a_case_copies_its_documents_manifest_last(
    source_db: Path,
    source_objects: casestore.InMemoryObjectTransport,
    tmp_path: Path,
) -> None:
    """An interrupted copy must not leave a manifest naming absent leaves."""
    order: list[str] = []

    class RecordingTransport(casestore.InMemoryObjectTransport):
        def put(self, key: str, body: bytes, *, if_absent: bool = False) -> None:
            order.append(key)
            super().put(key, body, if_absent=if_absent)

    dest_objects = RecordingTransport()
    _seed(
        source_db,
        source_objects,
        tmp_path,
        dest_objects=dest_objects,
        blob_transport=InMemoryFileTransport(),
        apply=True,
    )
    for case_id in SLICE_CASES:
        case_keys = [key for key in order if key.startswith(f"{case_id}/")]
        assert case_keys[-1] == f"{case_id}/documents/documents.json", case_keys


def test_objects_land_before_the_blob_is_published(
    source_db: Path,
    source_objects: casestore.InMemoryObjectTransport,
    tmp_path: Path,
) -> None:
    """A reader resolving the new pointer must always find the payloads.

    Pinned by making the blob publish fail: the objects must already be at the
    destination when it does, or the ordering has silently reversed.
    """

    class FailingBlobTransport(InMemoryFileTransport):
        def upload(self, key: str, source: Path) -> None:
            raise corpus_remote.CorpusRemoteError("upload refused")

    dest_objects = casestore.InMemoryObjectTransport()
    with pytest.raises(corpus_remote.CorpusRemoteError):
        _seed(
            source_db,
            source_objects,
            tmp_path,
            dest_objects=dest_objects,
            blob_transport=FailingBlobTransport(),
            apply=True,
        )
    # The store is ahead of the index — the safe direction, and the state the
    # next apply completes.
    assert dest_objects.objects
    for case_id in SLICE_CASES:
        assert f"{case_id}/case.json" in dest_objects.objects


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
        assert source_objects.objects == before
        # And the seed put the caller's transport back rather than clearing it:
        # clearing would silently re-enable a lazy build from settings.
        assert casestore.active_transport() is source_objects
    finally:
        casestore.reset_active_transport()


def test_the_mirror_override_restores_the_unbuilt_state() -> None:
    """A borrowed seam must not force a lazy build the process would have skipped."""
    casestore.reset_active_transport()
    assert not casestore.transport_is_built()
    with casestore.transport_override(None):
        pass
    # Still unbuilt: `transport_override` restored "not built yet", so the next
    # access is the lazy build it always would have been.
    assert not casestore.transport_is_built()


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
    """The command's environment: only the corpus root.

    Deliberately NO store URLs: the command's source is pinned on the command
    line, so it must run — and its rails must hold — with no ambient corpus
    variable at all.
    """
    monkeypatch.delenv("FEDCOURTS_CORPUS_REMOTE_URL", raising=False)
    monkeypatch.delenv("CORPUS_REMOTE_URL", raising=False)
    monkeypatch.delenv("FEDCOURTS_CASESTORE_URL", raising=False)
    monkeypatch.delenv("CASESTORE_URL", raising=False)
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))


_SOURCE_FLAGS = [
    "--source-remote",
    PROD_REMOTE,
    "--source-casestore",
    PROD_CASESTORE,
]


def test_the_command_refuses_a_destination_that_is_the_pinned_source(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _prod_env(monkeypatch, tmp_path)
    result = runner.invoke(
        app,
        [
            "corpus-seed-slice",
            *_SOURCE_FLAGS,
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


def test_the_command_requires_a_pinned_source(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """No source options, no run: the pin is required, with no ambient fallback."""
    _prod_env(monkeypatch, tmp_path)
    monkeypatch.setenv("FEDCOURTS_CORPUS_REMOTE_URL", PROD_REMOTE)
    monkeypatch.setenv("FEDCOURTS_CASESTORE_URL", PROD_CASESTORE)
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
    assert result.exit_code == 2
    assert "--source-remote" in result.output


def test_the_command_refuses_an_empty_pinned_source(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """An unset workflow variable resolves to the empty string — refused, never
    quietly re-based on whatever the environment holds."""
    _prod_env(monkeypatch, tmp_path)
    result = runner.invoke(
        app,
        [
            "corpus-seed-slice",
            "--source-remote",
            PROD_REMOTE,
            "--source-casestore",
            "",
            "--dest-remote",
            STAGING_REMOTE,
            "--dest-casestore",
            STAGING_CASESTORE,
            "--dockets",
            SLICE_CASES[0],
        ],
    )
    assert result.exit_code == 2
    assert "not pinned" in result.output


def test_the_command_ignores_a_flipped_environment(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """The `scripts/corpus-env staging` footgun, closed: a shell whose ambient
    variables name the staging pair cannot re-base the rail.

    The discriminator is which check stops the run. With the rail based on the
    ambient environment, a staging destination reads as "production" the
    moment the environment is flipped, and the run dies at the rail (exit 2).
    With the rail based on the pin, the flipped run sails past the rails and
    stops at the unrelated no-corpus check (exit 1) — while a destination
    equal to the *pin* is still refused (exit 2), whatever the environment.
    """
    _prod_env(monkeypatch, tmp_path)
    monkeypatch.setenv("FEDCOURTS_CORPUS_REMOTE_URL", STAGING_REMOTE)
    monkeypatch.setenv("FEDCOURTS_CASESTORE_URL", STAGING_CASESTORE)
    staging_destination = [
        "--dest-remote",
        STAGING_REMOTE,
        "--dest-casestore",
        STAGING_CASESTORE,
    ]
    allowed = runner.invoke(
        app,
        ["corpus-seed-slice", *_SOURCE_FLAGS, *staging_destination, "--dockets", SLICE_CASES[0]],
    )
    assert allowed.exit_code == 1, allowed.output
    assert "no corpus at" in allowed.output
    refused = runner.invoke(
        app,
        [
            "corpus-seed-slice",
            *_SOURCE_FLAGS,
            "--dest-remote",
            PROD_REMOTE,
            "--dest-casestore",
            PROD_CASESTORE,
            "--dockets",
            SLICE_CASES[0],
        ],
    )
    assert refused.exit_code == 2
    assert "names the pinned source" in refused.output


def test_the_command_refuses_a_pointer_override(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _prod_env(monkeypatch, tmp_path)
    sha = "0" * 64
    monkeypatch.setenv(
        "FEDCOURTS_CORPUS_POINTER",
        json.dumps({"key": f"index/sha256/{sha}", "schema_version": "1", "sha256": sha, "size": 1}),
    )
    result = runner.invoke(
        app,
        [
            "corpus-seed-slice",
            *_SOURCE_FLAGS,
            "--dest-remote",
            STAGING_REMOTE,
            "--dest-casestore",
            STAGING_CASESTORE,
            "--dockets",
            SLICE_CASES[0],
        ],
    )
    assert result.exit_code == 2
    assert "pointer override" in result.output


def test_the_command_refuses_a_stage_db_on_the_committed_corpus(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _prod_env(monkeypatch, tmp_path)
    result = runner.invoke(
        app,
        [
            "corpus-seed-slice",
            *_SOURCE_FLAGS,
            "--dest-remote",
            STAGING_REMOTE,
            "--dest-casestore",
            STAGING_CASESTORE,
            "--dockets",
            SLICE_CASES[0],
            "--stage-db",
            str(tmp_path / "corpus" / "corpus.db"),
        ],
    )
    assert result.exit_code == 2
    assert "--stage-db is the corpus blob" in result.output


def test_the_command_says_so_when_the_corpus_is_not_pulled(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _prod_env(monkeypatch, tmp_path)
    result = runner.invoke(
        app,
        [
            "corpus-seed-slice",
            *_SOURCE_FLAGS,
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
            *_SOURCE_FLAGS,
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
