"""The store mirror for cases whose document text reached only the blob.

Nothing reaches S3 here: the content store is
:class:`~fedcourtsai.casestore.InMemoryObjectTransport`, which is the transport
seam's own offline implementation, so what is under test is the pass's reading
of a real store rather than a stub of the reading.

Three things are worth stating about what is exercised. The population is read
by **direct SQL over the blob's ``documents`` table**, which inverts the reading
every other document pass takes, so these tests seed that table and never the
store's manifests. The seed itself runs with **no active transport**, because the
corpus's own dual-write would otherwise mirror as it wrote and build the
converged state instead of the gap. And the mirror writer is best-effort by
contract: it swallows a transport failure rather than raising, so the test that
matters most is the one whose store accepts every write and keeps none, where
the only thing between a clean-looking slice and the truth is the pass's own
re-probe.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import casestore, corpus
from fedcourtsai.cli import app
from fedcourtsai.pipeline.document_mirror import (
    blob_document_cases,
    blob_documents_for_case,
    mirror_stored_documents,
    store_serves_documents,
)

runner = CliRunner()

_FETCHED = date(2026, 5, 1)


class _DroppingTransport(casestore.InMemoryObjectTransport):
    """A store that accepts every write and keeps none.

    The shape a best-effort mirror cannot tell from a working store: nothing
    raises, so ``mirror_documents`` reports nothing and returns normally, and the
    only evidence the write did not land is a re-probe. A silently discarding
    bucket policy, a write to the wrong prefix, and a mirror withheld by the
    out-of-band pointer override all present exactly this way.
    """

    def put(self, key: str, body: bytes, *, if_absent: bool = False) -> None:
        self.puts += 1


def _document(
    case_id: str, kind: str = "petition", text: str = "petition text"
) -> corpus.CaseDocument:
    return corpus.CaseDocument(
        case_id=case_id,
        kind=kind,
        url=f"https://example.test/{case_id}/{kind}.pdf",
        entry_date="2026-04-01",
        fetched_at=_FETCHED,
        pages=3,
        text=text,
    )


@contextmanager
def _corpus(root: Path, documents: list[corpus.CaseDocument]) -> Iterator[sqlite3.Connection]:
    """A blob whose ``documents`` table carries ``documents``, seeded store-blind.

    The seed asserts that no transport is active, because the whole subject here
    is a blob holding text the store does not: a seed written while the store was
    reachable would mirror through the corpus's own dual-write and leave nothing
    in the class. Tests set their transport *inside* the block, after the seed.
    """
    assert casestore.active_transport() is None, "seed the blob with the store off"
    with corpus.connect(corpus.corpus_db_path(root)) as conn:
        corpus.upsert_documents(conn, documents)
        yield conn


def _store_holding(
    case_ids: list[str], documents: list[corpus.CaseDocument]
) -> casestore.InMemoryObjectTransport:
    """A store already carrying the mirror of ``case_ids`` — the *present* half."""
    transport = casestore.InMemoryObjectTransport()
    for case_id in case_ids:
        casestore.write_documents(
            transport, case_id, [d for d in documents if d.case_id == case_id]
        )
    return transport


# --- the population read ------------------------------------------------------


def test_the_population_is_the_blobs_own_documents_table(tmp_path: Path) -> None:
    """Read by direct SQL, grouped per case, with the byte size of the text.

    ``text_bytes`` is the size of what a mirror would upload, so it is counted in
    UTF-8 bytes rather than in the characters SQLite's own ``LENGTH()`` returns
    on a TEXT value — a multi-byte petition would otherwise be reported smaller
    than it is.
    """
    documents = [
        _document("scotus/1", "petition", "abc"),
        _document("scotus/1", "brief-in-opposition", "de"),
        # Two bytes per character, which is what separates the byte count from
        # the character count.
        _document("scotus/2", "petition", "ÿÿÿ"),
    ]
    with _corpus(tmp_path, documents) as conn:
        population = blob_document_cases(conn)
    assert [(case.case_id, case.rows, case.text_bytes) for case in population] == [
        ("scotus/1", 2, 5),
        ("scotus/2", 1, 6),
    ]


def test_the_documents_read_back_out_of_the_blob_are_the_stored_rows(tmp_path: Path) -> None:
    """The mirror's payload comes off the blob, not off the routed read."""
    documents = [_document("scotus/1", "petition"), _document("scotus/1", "brief-in-opposition")]
    with _corpus(tmp_path, documents) as conn:
        read = blob_documents_for_case(conn, "scotus/1")
    assert [d.kind for d in read] == ["brief-in-opposition", "petition"]
    assert {d.text for d in read} == {"petition text"}
    assert {d.pages for d in read} == {3}


def test_a_blob_predating_the_ocr_marker_reads_its_rows_as_extractions(tmp_path: Path) -> None:
    """The tolerance that keeps an older blob readable rather than fatal.

    ``ocr_derived`` post-dates the table, and a remote blob is served as-is, so a
    row that carries no such column must read as "not OCR" — the corpus's own
    reading of an optional column — instead of failing the whole document.
    """
    conn = sqlite3.connect(tmp_path / "pre-marker.db")
    conn.row_factory = sqlite3.Row
    try:
        conn.execute(
            "CREATE TABLE documents (case_id TEXT, kind TEXT, url TEXT, entry_date TEXT, "
            + "fetched_at TEXT, pages INTEGER, truncated INTEGER, text TEXT)"
        )
        conn.execute(
            "INSERT INTO documents VALUES (?,?,?,?,?,?,?,?)",
            ("scotus/1", "petition", "u", "2026-04-01", "2026-05-01", 3, 0, "body"),
        )
        (read,) = blob_documents_for_case(conn, "scotus/1")
    finally:
        conn.close()
    assert read.ocr_derived is False
    assert read.text == "body"


def test_a_blob_with_no_documents_table_reads_as_an_empty_population(tmp_path: Path) -> None:
    """A blob predating the documents migration is the wrong blob, not a crash."""
    conn = sqlite3.connect(tmp_path / "bare.db")
    conn.row_factory = sqlite3.Row
    try:
        assert blob_document_cases(conn) == ()
    finally:
        conn.close()


# --- the class ----------------------------------------------------------------


def test_the_class_is_the_cases_the_store_serves_no_document_for(tmp_path: Path) -> None:
    """Present and absent are told apart by the production read of the store."""
    documents = [_document(f"scotus/{n}") for n in (1, 2, 3)]
    transport = _store_holding(["scotus/2"], documents)
    with _corpus(tmp_path, documents) as conn:
        casestore.set_active_transport(transport)
        result = mirror_stored_documents(conn, apply=False)
    assert result.cases_with_blob_documents == 3
    assert result.present == 1
    assert result.absent == 2
    assert list(result.absent_cases) == ["scotus/1", "scotus/3"]
    assert result.absent_cases["scotus/1"].rows == 1
    # Nothing is verified on a dry run, so the whole class is what the next slice faces.
    assert result.remaining == 2


def test_a_case_carrying_only_an_empty_manifest_is_in_the_class(tmp_path: Path) -> None:
    """The blob holds its text and the store serves none of it — which is the defect.

    However the store came to look that way. A prefix listing would call this
    case present, because the empty manifest is itself an object under
    ``documents/``; the production read is what says the case is still dark.
    """
    documents = [_document("scotus/1")]
    transport = casestore.InMemoryObjectTransport()
    casestore.write_documents(transport, "scotus/1", [])
    assert transport.list_keys("scotus/1/documents/"), "the empty manifest is an object"
    with _corpus(tmp_path, documents) as conn:
        casestore.set_active_transport(transport)
        result = mirror_stored_documents(conn, apply=False)
    assert not store_serves_documents(transport, "scotus/1")
    assert result.present == 0
    assert result.absent == 1


def test_a_leaf_that_landed_without_its_manifest_is_not_verified(tmp_path: Path) -> None:
    """The failure a prefix listing would report as a clean, permanent success.

    ``merge_documents`` puts the text leaves before the manifest, so a manifest
    PUT that fails leaves keys under ``documents/`` and serves nothing. A listing
    would call the case verified and drop it from the class for good, while
    production went on reading it as empty. The production read is what keeps it
    in the class to be retried.
    """

    class _ManifestDropping(casestore.InMemoryObjectTransport):
        def put(self, key: str, body: bytes, *, if_absent: bool = False) -> None:
            if key.endswith("/documents/documents.json"):
                raise RuntimeError("manifest write refused")
            super().put(key, body, if_absent=if_absent)

    transport = _ManifestDropping()
    with _corpus(tmp_path, [_document("scotus/1")]) as conn:
        casestore.set_active_transport(transport)
        result = mirror_stored_documents(conn, apply=True, max_cases=1)
    assert transport.list_keys("scotus/1/documents/"), "the leaf landed"
    assert result.attempted == ["scotus/1"]
    assert result.verified == []
    assert result.unverified == ["scotus/1"]
    assert result.remaining == 1


def test_the_dry_run_writes_nothing(tmp_path: Path) -> None:
    """The whole population is probed and not one object is put."""
    documents = [_document(f"scotus/{n}") for n in (1, 2)]
    transport = casestore.InMemoryObjectTransport()
    with _corpus(tmp_path, documents) as conn:
        casestore.set_active_transport(transport)
        result = mirror_stored_documents(conn, apply=False)
    assert transport.puts == 0
    assert transport.objects == {}
    assert result.applied is False
    assert result.attempted == [] and result.verified == []
    assert result.bound is None


# --- the apply ----------------------------------------------------------------


def test_the_apply_mirrors_a_cases_whole_document_set_and_verifies_it(tmp_path: Path) -> None:
    documents = [_document("scotus/1"), _document("scotus/1", "brief-in-opposition")]
    transport = casestore.InMemoryObjectTransport()
    with _corpus(tmp_path, documents) as conn:
        casestore.set_active_transport(transport)
        result = mirror_stored_documents(conn, apply=True, max_cases=1)
    assert result.attempted == ["scotus/1"]
    assert result.verified == ["scotus/1"]
    assert result.unverified == []
    assert result.remaining == 0
    # Both kinds reached the store, not only the one whose absence named the case.
    assert {d.kind for d in casestore.read_documents(transport, "scotus/1")} == {
        "petition",
        "brief-in-opposition",
    }


def test_the_apply_mirrors_the_blobs_own_text_under_the_corpus_split(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The mode the lane runs in, and the one that tells the two writers apart.

    Off the split, ``documents_for_case`` reads the blob and
    ``mirror_documents_for_cases`` — which mirrors what that read returns — is
    behaviourally identical to the batch writer the pass uses. **On** it, the
    routed read answers from the content store, so the read-back writer would
    mirror an empty set and put an empty manifest over every case in the class,
    which the pass's own predicate then reads as permanently repaired. This is
    the only test that can fail if the writer regresses to it.

    Every field is asserted, not just the kinds: provisioning places a document
    by `entry_date` (falling back to `fetched_at`) and the OCR disclosure rides
    on `ocr_derived`, so a mirror that dropped either would move the cell's own
    timing cut without failing anything else here.
    """
    documents = [
        _document("scotus/1", "petition", "petition body"),
        _document("scotus/1", "brief-in-opposition", "opposition body"),
    ]
    transport = casestore.InMemoryObjectTransport()
    with _corpus(tmp_path, documents) as conn:
        monkeypatch.setenv("FEDCOURTS_CORPUS_SPLIT", "1")
        casestore.set_active_transport(transport)
        # The routed read is the store's now, and the store is empty — which is
        # exactly why the pass must not mirror what it returns.
        assert corpus.documents_for_case(conn, "scotus/1") == []
        result = mirror_stored_documents(conn, apply=True, max_cases=1)
    assert result.verified == ["scotus/1"]
    mirrored = {d.kind: d for d in casestore.read_documents(transport, "scotus/1")}
    assert set(mirrored) == {"petition", "brief-in-opposition"}
    petition = mirrored["petition"]
    assert petition.text == "petition body"
    assert petition.url == "https://example.test/scotus/1/petition.pdf"
    assert petition.entry_date == "2026-04-01"
    assert petition.fetched_at == _FETCHED
    assert petition.pages == 3
    assert petition.truncated is False
    assert petition.ocr_derived is False


def test_the_apply_takes_the_first_bound_cases_of_the_class(tmp_path: Path) -> None:
    """The slice is ``case_id``-ordered, so the untouched tail heads the next dispatch."""
    documents = [_document(f"scotus/{n}") for n in (1, 2, 3)]
    transport = casestore.InMemoryObjectTransport()
    with _corpus(tmp_path, documents) as conn:
        casestore.set_active_transport(transport)
        result = mirror_stored_documents(conn, apply=True, max_cases=2)
    assert result.attempted == ["scotus/1", "scotus/2"]
    assert result.verified == ["scotus/1", "scotus/2"]
    assert result.unreached == 1
    assert result.remaining == 1
    assert result.bound == 2
    assert not store_serves_documents(transport, "scotus/3")


def test_the_verification_catches_a_store_that_drops_every_write(tmp_path: Path) -> None:
    """The reading the whole ledger turns on.

    The mirror writer swallows transport failures by contract, so a store that
    accepts and discards raises nothing and returns normally. Without the
    re-probe this slice would report the same ``attempted`` a working one does,
    and a maintainer would read it as drained.
    """
    documents = [_document(f"scotus/{n}") for n in (1, 2)]
    transport = _DroppingTransport()
    with _corpus(tmp_path, documents) as conn:
        casestore.set_active_transport(transport)
        result = mirror_stored_documents(conn, apply=True, max_cases=2)
    assert result.attempted == ["scotus/1", "scotus/2"]
    assert result.verified == []
    assert result.unverified == ["scotus/1", "scotus/2"]
    # Nothing left the class, so the next slice faces exactly what this one did.
    assert result.remaining == result.absent == 2


def test_an_apply_with_no_bound_is_refused_before_the_population_is_read(tmp_path: Path) -> None:
    documents = [_document("scotus/1")]
    transport = casestore.InMemoryObjectTransport()
    with _corpus(tmp_path, documents) as conn:
        casestore.set_active_transport(transport)
        result = mirror_stored_documents(conn, apply=True)
    assert result.refused is True
    assert result.cases_with_blob_documents == 0
    assert transport.puts == 0


def test_no_content_store_is_reported_rather_than_a_class_of_everything(tmp_path: Path) -> None:
    """With nothing to probe, every case would read as absent — so none is reported."""
    documents = [_document("scotus/1")]
    with _corpus(tmp_path, documents) as conn:
        result = mirror_stored_documents(conn, apply=False)
    assert result.store_unavailable is True
    assert result.cases_with_blob_documents == 1
    assert result.absent == 0
    assert result.absent_cases == {}


# --- the command --------------------------------------------------------------


def _invoke(root: Path, *args: str) -> tuple[int, str]:
    result = runner.invoke(
        app, ["mirror-stored-documents", *args], env={"FEDCOURTS_CORPUS_ROOT": str(root)}
    )
    return result.exit_code, result.output


def _empty_corpus(root: Path) -> None:
    with corpus.connect(corpus.corpus_db_path(root)):
        pass


def test_the_command_refuses_a_blob_holding_no_document_rows(tmp_path: Path) -> None:
    """The wrong-blob refusal: a corpus written entirely under the split holds none."""
    _empty_corpus(tmp_path)
    code, output = _invoke(tmp_path)
    assert code == 1
    assert "no document rows" in output


def test_the_command_refuses_an_apply_with_no_slice_bound(tmp_path: Path) -> None:
    _empty_corpus(tmp_path)
    code, output = _invoke(tmp_path, "--apply")
    assert code == 2
    assert "--apply requires an explicit --max-cases" in output


def test_the_command_refuses_a_bound_offered_to_a_dry_run(tmp_path: Path) -> None:
    """Refused rather than ignored: the dry run's ledger is what the bound is read off."""
    _empty_corpus(tmp_path)
    code, output = _invoke(tmp_path, "--max-cases", "5")
    assert code == 2
    assert "--max-cases is read only with --apply" in output


def test_the_command_refuses_a_missing_corpus(tmp_path: Path) -> None:
    code, output = _invoke(tmp_path / "absent")
    assert code == 1
    assert "the corpus database is missing" in output


@pytest.mark.parametrize("apply", [True, False], ids=["apply", "dry-run"])
def test_the_command_refuses_when_no_content_store_is_configured(
    tmp_path: Path, apply: bool
) -> None:
    with _corpus(tmp_path, [_document("scotus/1")]):
        pass
    args = ("--apply", "--max-cases", "1") if apply else ()
    code, output = _invoke(tmp_path, *args)
    assert code == 1
    assert "no content store is configured" in output


def test_the_command_prints_the_ledger_a_dispatch_reads_back(tmp_path: Path) -> None:
    """The last line is the machine-readable ledger the workflow greps by field."""
    transport = casestore.InMemoryObjectTransport()
    with _corpus(tmp_path, [_document("scotus/1")]):
        pass
    casestore.set_active_transport(transport)
    code, output = _invoke(tmp_path)
    assert code == 0, output
    assert "scotus/1: 1 blob row(s)" in output
    assert output.strip().splitlines()[-1].startswith('{"applied"')


def test_the_command_applies_and_names_each_outcome(tmp_path: Path) -> None:
    """The apply's per-case lines, both polarities, from the command itself."""
    transport = _DroppingTransport()
    with _corpus(tmp_path, [_document("scotus/1"), _document("scotus/2")]):
        pass
    casestore.set_active_transport(transport)
    code, output = _invoke(tmp_path, "--apply", "--max-cases", "1")
    assert code == 0, output
    # The store took the write and kept nothing, which is the shape only the
    # re-probe reports — and the command has to name it rather than count it.
    assert "scotus/1: MIRRORED BUT NOT VERIFIED" in output
    assert "attempted 1 (bound 1); 1 case(s) beyond the bound" in output

    working = casestore.InMemoryObjectTransport()
    casestore.set_active_transport(working)
    code, output = _invoke(tmp_path, "--apply", "--max-cases", "2")
    assert code == 0, output
    assert "scotus/1: mirrored and verified" in output
    assert "scotus/2: mirrored and verified" in output
    assert "0 left for the next slice" in output
