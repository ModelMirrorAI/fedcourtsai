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
its docstring says why its fields are public. The one exception is
``ApplicationPlan``, which carries supremecourt.gov's served docket JSON, party
contact blocks included, under the narrow carve-out ``docs/data-sources.md``
(*PII stance*) records; a plan not shaped as those records and the fields
parsed from them is refused before it is written and again by its writer.

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

#: The largest handoff file a reader accepts. The biggest real one, the
#: opinion-record plan over the repair pass's six Terms with each writing's
#: text, is on the order of thirty megabytes.
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
        raise HandoffRefused(
            f"{path} is not a valid {model.__name__}: {exc.error_count()} problem(s), "
            f"the first a {first['type']} at {_safe_loc(first['loc'])}"
        ) from exc


def _safe_loc(loc: tuple[int | str, ...]) -> str:
    """Where a validation error sits, with every name in the path replaced by ``*``.

    A refusal is printed to a public step summary, and a name in pydantic's
    location can be the file's own text: an extra field, or a dict key. Only
    list positions are kept; the error ``type`` beside it is pydantic's own
    vocabulary. The message and the input are never printed for the same reason.
    """
    return ".".join(str(part) if isinstance(part, int) else "*" for part in loc) or "<root>"


def write_handoff(path: Path, model: BaseModel) -> None:
    """Write one handoff file (sorted keys, so a re-run is byte-stable)."""
    write_json(path, model)
