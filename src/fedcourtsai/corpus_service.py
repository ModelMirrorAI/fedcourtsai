"""The corpus query service: a localhost sidecar serving `query`/`open-events`.

Live cells retrieve corpus priors with `fedcourts query`, whose ranged backend
needs cloud credentials in the calling shell — credentials an agent shell
should not hold (and, under the Gemini CLI's env sanitizer, *cannot* hold: it
refuses to allowlist any credential-shaped variable name). This module makes
the retrieval surface credential-free for every engine: built so a workflow
step can start ``fedcourts corpus-serve`` with the credentials scoped to that
step, while the agents' CLI — pointed at it by
``FEDCOURTS_CORPUS_SERVICE_URL`` with the ``service`` backend — forwards whole
requests over localhost HTTP. Same command, same flags, same output bytes, no
credential in reach.

Design, deliberately minimal:

- **Single-threaded stdlib server** (`http.server`), one long-lived
  ``corpus.connect_readonly`` connection for the process life. Nothing in the
  read stack is thread-safe (the ranged VFS block cache, ``sqlite3``'s
  same-thread default, the read counters), and single-threading needs zero
  locks; a cell's ~25 sequential queries queue happily in the listen backlog.
  The held connection is also the egress win: the ranged backend's block
  cache stays warm across the whole cell instead of refetching the schema
  pages per CLI invocation.
- **Wire contract**: pydantic models below, ``/v1/`` path prefix plus a
  ``schema_version`` literal. Both ends always come from the same checkout
  (one repo clone launches the sidecar and the CLI in one job), so this is an
  internal protocol — deliberately *not* registered in the exportable data
  schemas.
- **Read stats per request**: the ranged connection's cumulative counters are
  snapshotted around each query and the delta returned as ``reads``, so the
  CLI keeps printing the ``ranged corpus reads: N GET(s), M byte(s)`` stderr
  line the prompts tell agents to record. A warm cache legitimately reports
  ``0 GET(s)`` — still evidence of a transfer-free read. ``reads`` is null on
  the local backend, matching the CLI's silent local path.

Failure contract: the server returns 400 for a request the models reject
(contract drift — near-impossible same-checkout) and 500 naming only the
exception *type* for a backend failure (the detail goes to the sidecar log:
backend errors can embed the remote URL, and the client echoes the wire body
into workflow logs); the client wraps any transport or non-200 outcome in
:class:`CorpusServiceError`, which the CLI reports to stderr and exits 1 —
the same degraded-cell contract as any failed query today.
"""

from __future__ import annotations

import contextlib
import json
import logging
import sqlite3
from collections.abc import Callable, Iterator
from contextlib import AbstractContextManager
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Literal, cast

import httpx
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from . import corpus, corpus_ranged, store

logger = logging.getLogger(__name__)

SCHEMA_VERSION = "1.0"

# One fixed port for the workflow wiring; `create_server(port=0)` picks an
# ephemeral one for tests and ad-hoc local use.
DEFAULT_PORT = 8377

_CLIENT_TIMEOUT_SECONDS = 30.0

# Real requests are a few hundred bytes; anything bigger is a bug or abuse.
_MAX_REQUEST_BYTES = 1_048_576

# Server-side ceiling on one response's row count: the caller's shell is the
# only expected client, but an unbounded limit would build every matching
# row's full opinion text into one in-memory JSON body.
MAX_QUERY_LIMIT = 500


class CorpusServiceError(RuntimeError):
    """The service could not be reached or refused the request."""


class ReadCounters(BaseModel):
    """The ranged transfer evidence for one request (see module docstring)."""

    model_config = ConfigDict(extra="forbid")

    gets: int
    bytes: int


class QueryRequest(BaseModel):
    """One forwarded ``fedcourts query`` invocation."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1.0"]
    query: corpus.PriorQuery
    limit: int = Field(ge=0, le=MAX_QUERY_LIMIT)
    full: bool


class QueryResponse(BaseModel):
    """Ranked prior rows, pre-shaped so the wire shape equals the printed shape."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1.0"]
    rows: list[dict[str, object]]
    reads: ReadCounters | None


class OpenEventsRequest(BaseModel):
    """One forwarded ``fedcourts open-events`` invocation."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1.0"]
    court: str
    docket: int


class OpenEventsResponse(BaseModel):
    """A case's unresolved (predictable) event ids."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1.0"]
    event_ids: list[str]
    reads: ReadCounters | None


class CorpusService:
    """The request handlers, bound to one lazily-opened long-lived connection.

    The connection opens on the *first request* — i.e. in the serving thread —
    not at construction: ``sqlite3`` connections refuse cross-thread use, and
    the server that owns this service may (in tests, or a future embedding) be
    driven from a different thread than the one that built it. Single-threaded
    serving means every request thereafter runs in that same thread. It also
    makes ``/healthz`` honest: a green health check proves the corpus is
    actually readable, not just that the socket is bound.
    """

    def __init__(
        self,
        opener: Callable[[], AbstractContextManager[corpus.ReadConnection]],
        *,
        backend: str,
    ) -> None:
        self._opener = opener
        self._backend = backend
        self._stack = contextlib.ExitStack()
        self._conn: corpus.ReadConnection | None = None

    def _connection(self) -> corpus.ReadConnection:
        if self._conn is None:
            self._conn = self._stack.enter_context(self._opener())
        return self._conn

    def close(self) -> None:
        self._stack.close()
        self._conn = None

    @staticmethod
    def _snapshot(conn: corpus.ReadConnection) -> tuple[int, int] | None:
        if isinstance(conn, corpus_ranged.RangedConnection):
            stats = conn.stats
            return (stats.gets, stats.bytes_fetched)
        return None

    @classmethod
    def _counters_since(
        cls, conn: corpus.ReadConnection, before: tuple[int, int] | None
    ) -> ReadCounters | None:
        if before is None:
            return None
        after = cls._snapshot(conn)
        assert after is not None  # the connection cannot change class mid-request
        return ReadCounters(gets=after[0] - before[0], bytes=after[1] - before[1])

    def _baseline(self) -> tuple[corpus.ReadConnection, tuple[int, int] | None]:
        """The connection plus this request's read-stats baseline.

        A request that itself triggers the lazy open is charged the open's
        transfer too (the counters start at zero on a fresh connection), so a
        cold sidecar's first evidence line carries the true cost instead of
        attributing it to no request. When the health check opens the
        connection first — the workflow flow — the startup transfer precedes
        every query and shows in the sidecar log instead.
        """
        opened = self._conn is None
        conn = self._connection()
        before = self._snapshot(conn)
        if opened and before is not None:
            before = (0, 0)
        return conn, before

    def query(self, request: QueryRequest) -> QueryResponse:
        conn, before = self._baseline()
        priors = corpus.retrieve_priors(conn, request.query, limit=request.limit)
        rows = [corpus.prior_payload(row, full=request.full) for row in priors]
        return QueryResponse(
            schema_version=SCHEMA_VERSION, rows=rows, reads=self._counters_since(conn, before)
        )

    def open_events(self, request: OpenEventsRequest) -> OpenEventsResponse:
        conn, before = self._baseline()
        event_ids = store.open_event_ids(conn, request.court, request.docket)
        return OpenEventsResponse(
            schema_version=SCHEMA_VERSION,
            event_ids=event_ids,
            reads=self._counters_since(conn, before),
        )

    def health(self) -> dict[str, object]:
        self._connection()  # a green health check proves the corpus opens
        return {"status": "ok", "backend": self._backend, "schema_version": SCHEMA_VERSION}


class _CorpusHTTPServer(HTTPServer):
    """The stdlib server plus the service whose connection it owns."""

    service: CorpusService

    def server_close(self) -> None:
        super().server_close()
        self.service.close()


class _Handler(BaseHTTPRequestHandler):
    # A stalled client (headers sent, body never arrives) would otherwise
    # wedge the single-threaded server — health endpoint included — until the
    # job timeout; the stdlib honors this per-connection socket timeout and
    # drops the connection instead.
    timeout = 30

    # Route the default stderr chatter to the module logger (the sidecar log),
    # never stdout — the CLI contract owns stdout.
    def log_message(self, format: str, *args: object) -> None:
        # The request line is client-supplied bytes; strip control characters
        # so a crafted path cannot forge extra lines (or terminal escapes) in
        # the sidecar log, which the workflow replays into the job log.
        message = "".join(
            char if char.isprintable() or char == " " else "?" for char in format % args
        )
        logger.info("%s - %s", self.address_string(), message)

    def _send_json(self, status: int, payload: str) -> None:
        body = payload.encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_failure(self, context: str, exc: Exception) -> None:
        # The full detail goes to the sidecar log only: a ranged backend error
        # can embed the remote URL, and the client echoes this body into
        # workflow logs — so the wire carries the exception type, not its text.
        logger.exception("%s failed", context)
        self._send_json(500, json.dumps({"error": f"{type(exc).__name__} (see the sidecar log)"}))

    @property
    def _service(self) -> CorpusService:
        return cast(_CorpusHTTPServer, self.server).service

    def do_GET(self) -> None:
        if self.path == "/healthz":
            try:
                health = self._service.health()
            except Exception as exc:  # the corpus would not open: a 500, not a crash
                self._send_failure("health check", exc)
                return
            self._send_json(200, json.dumps(health))
            return
        self._send_json(404, json.dumps({"error": f"unknown path {self.path!r}"}))

    def do_POST(self) -> None:
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._send_json(400, json.dumps({"error": "malformed Content-Length"}))
            return
        if length < 0 or length > _MAX_REQUEST_BYTES:
            self._send_json(413, json.dumps({"error": f"Content-Length {length} out of bounds"}))
            return
        body = self.rfile.read(length)
        try:
            if self.path == "/v1/query":
                response: BaseModel = self._service.query(QueryRequest.model_validate_json(body))
            elif self.path == "/v1/open-events":
                response = self._service.open_events(OpenEventsRequest.model_validate_json(body))
            else:
                self._send_json(404, json.dumps({"error": f"unknown path {self.path!r}"}))
                return
        except ValidationError as exc:
            self._send_json(400, json.dumps({"error": str(exc)}))
            return
        except Exception as exc:  # a request must never kill the server
            self._send_failure(f"request to {self.path}", exc)
            return
        self._send_json(200, response.model_dump_json())


def create_server(
    db_path: Path,
    *,
    backend: corpus.CorpusBackend | None = None,
    host: str = "127.0.0.1",
    port: int = 0,
) -> _CorpusHTTPServer:
    """Build the server; the caller runs ``serve_forever``.

    ``port=0`` binds an ephemeral port (tests, ad-hoc local runs); the bound
    address is on ``server_address``. The corpus connection opens lazily on
    the first request (see :class:`CorpusService`); ``server_close()`` closes
    it with the socket.
    """
    effective = corpus.resolve_backend(backend)
    server = _CorpusHTTPServer((host, port), _Handler)
    opener: Callable[[], AbstractContextManager[corpus.ReadConnection]]
    if effective == "local":
        opener = lambda: _local_reader(db_path)  # noqa: E731 - a deferred-open thunk
    else:
        opener = lambda: corpus.connect_readonly(db_path, backend=effective)  # noqa: E731
    server.service = CorpusService(opener, backend=effective)
    return server


@contextlib.contextmanager
def _local_reader(db_path: Path) -> Iterator[corpus.ReadConnection]:
    """A read-only local connection safe across the server's thread boundary.

    ``corpus.connect`` is the writer-shaped open (schema creation, migrations,
    a same-thread ``sqlite3`` guard); the service wants none of that — it must
    not write to a file it only serves, and its connection is *opened* on the
    serving thread but *closed* by ``server_close`` on the launcher's thread,
    which the stdlib guard forbids. Requests themselves all run on the single
    serving thread, so disabling the guard trades away nothing.
    """
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.create_function("norm_dn", 1, corpus.normalize_docket_number, deterministic=True)
    try:
        yield conn
    finally:
        conn.close()


def _post(base_url: str, path: str, request: BaseModel) -> httpx.Response:
    url = base_url.rstrip("/") + path
    try:
        response = httpx.post(
            url,
            content=request.model_dump_json(),
            headers={"Content-Type": "application/json"},
            timeout=_CLIENT_TIMEOUT_SECONDS,
        )
    except httpx.HTTPError as exc:
        raise CorpusServiceError(
            f"corpus service at {base_url} is unreachable — is the sidecar "
            f"running? (fedcourts corpus-serve): {exc}"
        ) from exc
    if response.status_code != 200:
        detail = response.text[:500]
        raise CorpusServiceError(
            f"corpus service at {base_url} rejected {path} ({response.status_code}): {detail}"
        )
    return response


def client_query(
    base_url: str, query: corpus.PriorQuery, *, limit: int, full: bool
) -> QueryResponse:
    """Forward one ``query`` invocation; raises :class:`CorpusServiceError`."""
    try:
        request = QueryRequest(schema_version=SCHEMA_VERSION, query=query, limit=limit, full=full)
    except ValidationError as exc:
        # A limit past the service ceiling, for instance — a clean diagnosis,
        # not a traceback.
        raise CorpusServiceError(f"invalid corpus service request: {exc}") from exc
    return QueryResponse.model_validate_json(_post(base_url, "/v1/query", request).content)


def client_open_events(base_url: str, court: str, docket: int) -> OpenEventsResponse:
    """Forward one ``open-events`` invocation; raises :class:`CorpusServiceError`."""
    request = OpenEventsRequest(schema_version=SCHEMA_VERSION, court=court, docket=docket)
    return OpenEventsResponse.model_validate_json(
        _post(base_url, "/v1/open-events", request).content
    )
