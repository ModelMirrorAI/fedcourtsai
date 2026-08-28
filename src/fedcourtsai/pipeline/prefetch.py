"""Bounded, order-preserving prefetch of a per-case corpus read.

Several corpus-wide passes are shaped the same way: walk an ordered population
of cases, read one payload per case, then run serial, ordered logic over what
came back. Where payload reads are offloaded to the per-case content store
(:func:`corpus.payload_reads_offloaded`) that read is a network GET, and its
latency is the whole cost of the pass — a serial walk of a population in the
thousands is what turns a dispatched sweep into a job-cap cancellation. Where
they are not, the read is local SQLite on the caller's connection, which must
stay on one thread.

:func:`prefetch_by_case` is that fan-out, once, so a pass supplies only its
population and its per-case read. Four constraints are load-bearing, and each
is why the shape is what it is rather than a plain :func:`map`:

- **The gate decides the schedule.** Pooled reads are sound only against the
  registered :class:`~fedcourtsai.corpus.PayloadReadSource`, whose Protocol
  owes concurrent-read safety; the SQLite fallback stays serial because the
  connection is single-thread. The helper consults the gate itself, so no
  caller can pool a connection read by forgetting to.
- **The first read is a warm-up, on the calling thread, before the pool
  exists.** The content-store source builds its client lazily on first use
  behind a broad catch that caches the outcome, so a pool-first call would
  race N constructions and a losing thread's cached failure would silently
  empty the pass. Client *calls* tolerate threads; construction does not.
- **Results come back in input order.** Callers classify and write in
  population order, so pooled and serial passes have to produce identical
  output — pairing by position (a strict :func:`zip`, which would raise rather
  than silently truncate if the result stream ever drifted from the input) is
  what makes that true.
- **The pool's lifetime is the ``with`` block, not the iterator's.** Reads run
  on threads a suspended generator would keep alive long past an abort, so the
  entry point is a context manager: leaving the block — normally, or on an
  exception raised by the *consumer* — cancels every unstarted read and shuts
  the pool down before the caller's handler runs, so an abandoned pass costs
  at most the reads already in flight, never the whole population's. The
  yielded stream is dead once the block exits: iterating it outside yields
  nothing, so consume inside the block.

Two properties a caller should not misread. The pool is bounded but its
*submission* is not: every read is queued once the consumer starts iterating,
so results the consumer has not reached yet are held in memory — consuming
them frees each one, but peak retention is however far the readers race
ahead, and a population of large payloads pays for that. And the consumer
runs on the calling thread: only ``read`` is handed to workers, so a loop
body may touch the caller's connection and filesystem freely.

An exception from a read propagates to the caller and ends the pass. Any
partial-result policy is the caller's, not this helper's.
"""

from __future__ import annotations

from collections.abc import Callable, Generator, Iterator, Sequence
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager

from .. import corpus

# Concurrent content-store readers for a prefetch pass. Sixteen bounded workers
# hold a full-population scan to minutes without meaningfully loading the store;
# the bound is what keeps a sweep from behaving like an unthrottled client
# against it.
PREFETCH_READERS = 16


@contextmanager
def prefetch_by_case[T](
    case_ids: Sequence[str],
    read: Callable[[str], T],
    *,
    thread_name_prefix: str,
) -> Iterator[Iterator[tuple[str, T]]]:
    """Yield an iterator of ``(case_id, read(case_id))`` pairs, in input order.

    Reads run on a bounded pool of :data:`PREFETCH_READERS` workers when
    payload reads are offloaded, and serially on the calling thread when they
    are not — see the module docstring for why the gate, the warm-up read, the
    ordering, and this block's scope are not incidental. ``read`` must be safe
    to call from a worker thread under the offloaded schedule (a
    :class:`~fedcourtsai.corpus.PayloadReadSource` call is; anything touching
    the caller's :mod:`sqlite3` connection is not). The loop body carries no
    such constraint: it resumes on the calling thread.

    ``thread_name_prefix`` names the pass in thread names, so a stack dump from
    a stuck sweep says which one is holding the readers.
    """
    stream = _pairs(case_ids, read, thread_name_prefix=thread_name_prefix)
    try:
        yield stream
    finally:
        # Closing the generator throws into its suspended `yield`, so the
        # pool's own `with` runs here — at the exit point — rather than
        # whenever the abandoned generator is collected.
        stream.close()


def _pairs[T](
    case_ids: Sequence[str],
    read: Callable[[str], T],
    *,
    thread_name_prefix: str,
) -> Generator[tuple[str, T], None, None]:
    """The schedule itself; :func:`prefetch_by_case` owns its lifetime — hence
    :class:`~collections.abc.Generator`, whose ``close`` is what shuts the pool
    down at the block's exit."""
    if not case_ids or not corpus.payload_reads_offloaded():
        for case_id in case_ids:
            yield case_id, read(case_id)
        return
    # Warm-up: constructs the source's lazy client here, on the calling
    # thread, before any worker can race a second construction.
    first = read(case_ids[0])
    tail = case_ids[1:]
    # Not `with ThreadPoolExecutor(...)`: Executor.__exit__ is shutdown with
    # no cancellation, which drains every already-submitted read after an
    # abort — the pool would finish the whole population's GETs for a pass
    # that has given up. Cancelling the unstarted futures bounds an abort's
    # cost to the reads in flight.
    pool = ThreadPoolExecutor(max_workers=PREFETCH_READERS, thread_name_prefix=thread_name_prefix)
    try:
        yield case_ids[0], first
        fetched = pool.map(read, tail)
        yield from zip(tail, fetched, strict=True)
    finally:
        pool.shutdown(wait=True, cancel_futures=True)
