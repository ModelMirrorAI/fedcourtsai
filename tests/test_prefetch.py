"""The bounded per-case prefetch helper: schedule, ordering, and the warm-up.

What these pin is not "reads happen" but *how* they are scheduled — the four
constraints the helper exists to hold: the offload gate picks pooled or serial,
the first read runs on the calling thread before any worker exists, results
come back paired with their case in input order however the pool completes, and
the readers are joined when the block exits however it exits.
"""

from __future__ import annotations

import threading
import time
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date
from typing import Any

import pytest

from fedcourtsai import corpus
from fedcourtsai.pipeline.prefetch import PREFETCH_READERS, prefetch_by_case

# Long enough that a real hang fails the test instead of wedging the suite,
# short enough that it never fires on a loaded runner doing the right thing.
_WAIT_SECONDS = 30.0


class _InertReadSource:
    """A payload read source that serves nothing.

    The helper's schedule is keyed on :func:`corpus.payload_reads_offloaded`,
    not on what the source returns — the per-case read is the caller's
    callable — so registering this is exactly enough to turn the gate on.
    """

    def latest_snapshot(self, case_id: str) -> tuple[date, dict[str, Any]] | None:
        return None

    def snapshot_at(self, case_id: str, *, before: date) -> tuple[date, dict[str, Any]] | None:
        return None

    def latest_live_snapshot(self, case_id: str) -> tuple[date, dict[str, Any]] | None:
        return None

    def documents_for_case(self, case_id: str) -> list[corpus.CaseDocument]:
        return []

    def opinion_text(self, case_id: str) -> str | None:
        return None


@contextmanager
def _offloaded(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Turn the payload-read offload gate on for the block.

    Reading the private registry is the only way to put back the casestore
    singleton registered at import (there is no public getter).
    """
    monkeypatch.setenv("FEDCOURTS_CORPUS_SPLIT", "1")
    previous = corpus._READ_SOURCE.get("source")
    corpus.set_payload_read_source(_InertReadSource())
    try:
        assert corpus.payload_reads_offloaded()
        yield
    finally:
        corpus.set_payload_read_source(previous)


class _RecordingReader:
    """Records every read in call order with the thread it ran on, and the
    worker threads alive at the moment it ran."""

    def __init__(self, *, thread_name_prefix: str) -> None:
        self._prefix = thread_name_prefix
        self._lock = threading.Lock()
        self.calls: list[str] = []
        self.threads: dict[str, int] = {}
        self.workers_alive: dict[str, int] = {}

    def read(self, case_id: str) -> str:
        alive = sum(1 for t in threading.enumerate() if t.name.startswith(self._prefix))
        with self._lock:
            self.calls.append(case_id)
            self.threads[case_id] = threading.get_ident()
            self.workers_alive[case_id] = alive
        return f"payload:{case_id}"


def _cases(count: int) -> list[str]:
    return [f"scotus/{n}" for n in range(count)]


def test_serial_fallback_reads_in_order_on_the_calling_thread(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """With reads served from SQLite the connection must stay on one thread, so
    the helper never pools: every read is on the caller's thread, in order."""
    monkeypatch.delenv("FEDCOURTS_CORPUS_SPLIT", raising=False)
    assert not corpus.payload_reads_offloaded()
    case_ids = _cases(5)
    reader = _RecordingReader(thread_name_prefix="test-serial")
    with prefetch_by_case(case_ids, reader.read, thread_name_prefix="test-serial") as fetched:
        got = list(fetched)
    assert got == [(case_id, f"payload:{case_id}") for case_id in case_ids]
    assert reader.calls == case_ids
    assert set(reader.threads.values()) == {threading.get_ident()}
    # No pool is built at all, so no worker thread ever carried a read.
    assert set(reader.workers_alive.values()) == {0}


def test_warm_up_read_precedes_every_worker(monkeypatch: pytest.MonkeyPatch) -> None:
    """The offloaded source builds its client lazily on first use and caches
    the outcome, so the first read must complete on the calling thread before a
    worker exists to race a second construction. The tail then runs off-thread."""
    case_ids = _cases(8)
    reader = _RecordingReader(thread_name_prefix="test-warmup")
    with (
        _offloaded(monkeypatch),
        prefetch_by_case(case_ids, reader.read, thread_name_prefix="test-warmup") as fetched,
    ):
        got = list(fetched)
    assert got == [(case_id, f"payload:{case_id}") for case_id in case_ids]
    first = case_ids[0]
    assert reader.calls[0] == first
    assert reader.threads[first] == threading.get_ident()
    # The load-bearing half: no thread of this pass's pool was alive yet.
    assert reader.workers_alive[first] == 0
    tail_threads = {reader.threads[case_id] for case_id in case_ids[1:]}
    assert threading.get_ident() not in tail_threads
    assert all(reader.workers_alive[case_id] > 0 for case_id in case_ids[1:])


def test_offloaded_results_keep_input_order_when_reads_finish_out_of_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Callers classify and write in population order, so a pooled pass has to
    produce the same sequence a serial one would. The first tail read is held
    until the last one has finished, so completion order is provably not input
    order — and the yielded pairing is input order regardless."""
    case_ids = _cases(6)
    held, released = case_ids[1], case_ids[-1]
    last_read = threading.Event()
    completed: list[str] = []
    lock = threading.Lock()

    def read(case_id: str) -> str:
        if case_id == released:
            last_read.set()
        elif case_id == held:
            assert last_read.wait(_WAIT_SECONDS), "the pool never reached the last case"
        with lock:
            completed.append(case_id)
        return f"payload:{case_id}"

    with (
        _offloaded(monkeypatch),
        prefetch_by_case(case_ids, read, thread_name_prefix="test-order") as fetched,
    ):
        got = list(fetched)

    assert got == [(case_id, f"payload:{case_id}") for case_id in case_ids]
    assert completed.index(released) < completed.index(held)


def test_offloaded_pairs_every_case_exactly_once(monkeypatch: pytest.MonkeyPatch) -> None:
    """One read per case, one yielded pair per case, positionally paired.

    Pairing is by position — the strict :func:`zip` inside the helper — so a
    result stream that ever ran short or long of its input would raise here
    rather than silently mis-pair payloads with cases or truncate the pass.
    Repeated ids make the point that positions, not identities, are matched.
    """
    case_ids = [*_cases(4), "scotus/1", "scotus/1"]
    reader = _RecordingReader(thread_name_prefix="test-pairs")
    with (
        _offloaded(monkeypatch),
        prefetch_by_case(case_ids, reader.read, thread_name_prefix="test-pairs") as fetched,
    ):
        got = list(fetched)
    assert len(got) == len(case_ids)
    assert [case_id for case_id, _ in got] == case_ids
    assert all(payload == f"payload:{case_id}" for case_id, payload in got)
    assert len(reader.calls) == len(case_ids)


def test_empty_population_reads_nothing(monkeypatch: pytest.MonkeyPatch) -> None:
    """No cases means no warm-up read and no pool — the empty pass is free."""
    reader = _RecordingReader(thread_name_prefix="test-empty")
    with (
        _offloaded(monkeypatch),
        prefetch_by_case([], reader.read, thread_name_prefix="test-empty") as fetched,
    ):
        assert list(fetched) == []
    assert reader.calls == []


def test_a_failing_read_propagates(monkeypatch: pytest.MonkeyPatch) -> None:
    """A read that raises ends the pass; the helper has no partial-result
    policy of its own, so the caller's abort semantics survive the pooling."""

    def read(case_id: str) -> str:
        if case_id == "scotus/3":
            raise RuntimeError("content store refused")
        return f"payload:{case_id}"

    with (
        _offloaded(monkeypatch),
        pytest.raises(RuntimeError, match="content store refused"),
        prefetch_by_case(_cases(6), read, thread_name_prefix="test-raise") as fetched,
    ):
        list(fetched)


def test_a_raising_consumer_shuts_the_pool_down(monkeypatch: pytest.MonkeyPatch) -> None:
    """Leaving the block ends the pass, whoever raised.

    Every read is submitted once the consumer starts iterating, so a consumer
    that gives up early leaves the whole reader pool mid-population. The
    context manager closes the stream at the exit point, so the pool is joined
    before the caller's handler runs — not whenever a traceback-held generator
    happens to be collected, which would leave the readers issuing GETs for a
    sweep that has already aborted.
    """
    prefix = "test-abort"

    def read(case_id: str) -> str:
        time.sleep(0.01)
        return f"payload:{case_id}"

    reads = 0
    lock = threading.Lock()

    def counted(case_id: str) -> str:
        nonlocal reads
        with lock:
            reads += 1
        return read(case_id)

    with (
        _offloaded(monkeypatch),
        pytest.raises(RuntimeError, match="give up"),
        prefetch_by_case(_cases(200), counted, thread_name_prefix=prefix) as fetched,
    ):
        for seen, _ in enumerate(fetched):
            if seen == 1:
                raise RuntimeError("give up")
    assert [t.name for t in threading.enumerate() if t.name.startswith(prefix)] == []
    # The abort also CANCELS the unstarted reads: without cancel_futures the
    # join above would first drain all 200 — the whole population's GETs spent
    # on a pass that gave up. The exact residue races (a worker can grab one
    # more future between finishing and the cancellation), so the bound is
    # slack but decisive: a drain reads all 200, cancellation stays near the
    # in-flight window.
    assert reads < 5 * PREFETCH_READERS


def test_a_breaking_consumer_gets_the_same_teardown(monkeypatch: pytest.MonkeyPatch) -> None:
    "A bare ``break`` is the likelier real-world abort; same exit, same bound."
    prefix = "test-break"
    reads = 0
    lock = threading.Lock()

    def read(case_id: str) -> str:
        nonlocal reads
        with lock:
            reads += 1
        time.sleep(0.01)
        return f"payload:{case_id}"

    with (
        _offloaded(monkeypatch),
        prefetch_by_case(_cases(200), read, thread_name_prefix=prefix) as fetched,
    ):
        for seen, _ in enumerate(fetched):
            if seen == 1:
                break
    assert [t.name for t in threading.enumerate() if t.name.startswith(prefix)] == []
    assert reads < 5 * PREFETCH_READERS  # same slack-but-decisive bound as the raise test
