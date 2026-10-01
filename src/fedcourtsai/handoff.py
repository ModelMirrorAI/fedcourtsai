"""The JSON files that carry a run-repair pass across its credential boundary.

A maintenance pass that fetches and parses third-party content — a Court PDF,
a docket JSON — runs that parse in a job holding no credential at all, and the
jobs on either side of it talk to it only through files of the shapes defined
beside each pass:

- a **projection**: the few public facts the parse needs from the corpus (a
  docket number per ledger case, the documents already recorded, a Term's
  stored application serials), written by a read-only job that holds the
  read-only role and parses nothing fetched;
- a **plan**: what the parse read, as structured rows, written by the
  credential-free job and applied by a writer job that holds the write
  credentials and fetches nothing.

Both travel as GitHub Actions run artifacts, which on a public repository any
signed-in user can download while they exist, so a model that crosses carries
public Court data only — never a corpus row, snapshot or stored document — and
its docstring says why its fields are public. The one that could not
(``ApplicationPlan``, which carries served docket JSON with party contact
details) is held back by the workflow and says so.

The receiving side treats a file as untrusted input: it is size-capped, parsed
by its pydantic model (``extra="forbid"``, a literal ``format`` name and
``version``), and refused whole on any departure, before anything is written.
What the model cannot check — that a row names an outcome in the ledger, that a
record conforms to its source's registration — the pass's own apply re-checks
against the state it is about to write.
"""

from __future__ import annotations

from pathlib import Path
from typing import Final

from pydantic import BaseModel, ValidationError

from .serialize import write_json

#: The largest handoff file a reader accepts. The biggest real one, a Term's
#: served application dockets, is on the order of ten megabytes.
MAX_HANDOFF_BYTES: Final = 64 * 1024 * 1024


class HandoffRefused(ValueError):
    """A handoff file that is missing, oversized, malformed or inconsistent."""


def read_handoff[M: BaseModel](
    path: Path, model: type[M], *, max_bytes: int = MAX_HANDOFF_BYTES
) -> M:
    """``path`` parsed as ``model``, or :class:`HandoffRefused` saying why not."""
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise HandoffRefused(f"{path}: cannot be read: {exc.strerror or exc}") from exc
    if size > max_bytes:
        raise HandoffRefused(f"{path}: {size} bytes, above the {max_bytes}-byte handoff cap")
    try:
        return model.model_validate_json(path.read_bytes())
    except ValidationError as exc:
        first = exc.errors()[0]
        where = ".".join(str(part) for part in first["loc"]) or "<root>"
        raise HandoffRefused(
            f"{path} is not a valid {model.__name__}: {exc.error_count()} problem(s), "
            f"the first at {where}: {first['msg']}"
        ) from exc


def write_handoff(path: Path, model: BaseModel) -> None:
    """Write one handoff file (sorted keys, so a re-run is byte-stable)."""
    write_json(path, model)
