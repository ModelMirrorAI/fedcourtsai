"""Run the censuses the pending freeze-record placeholders wait on, as one corpus check.

Declared in a pull request's description as

    ```corpus-check
    uv run python scripts/checks/freeze_record_census_fills.py
    ```

it runs five censuses in sequence, each as its own subprocess with its own
temporary `CHECK_SUMMARY`, and appends each one's summary to the file named by
`CHECK_SUMMARY` under a heading naming the `docs/freeze-record.md` entry whose
free-text census placeholder it fills:

- `withheld_petitioner_census.py` — the withheld-petitioner-block entry;
- `side_motion_census.py` — the side-motion carve-out entry (its pass 2 is the
  placeholder's figure);
- `post_conference_census.py` — the post-conference set-aside entry;
- `increment_timing_census.py` — the increment-timing entry;
- `interim_partial_moot_census.py` — the interim partial/moot reading entry.

`fedcourts corpus-info` runs once at the top for the corpus vintage, beside the
ledger vintage the censuses that read `data/` see (the newest prediction and
evaluation run ids at the checkout). A census whose own `corpus-info` block
matches the top one has it replaced by a back-reference.

A census that fails, times out or writes nothing is reported under its
heading as `FAILED` and the rest still run; the wrapper exits non-zero naming
each one that failed, and a census's own exit code is what marks it: each
exits non-zero when its figures cannot be read as they stand (the side-motion
and withheld-petitioner censuses name the self-checks that do this). A
`corpus-info` that fails, times out or finds no corpus is a failure too.

The lane posts the summary as a PR comment clamped to 50,000 bytes and stops a
check at 30 minutes (docs/corpus-check.md). So the whole summary is budgeted
to `--max-bytes`, the lane's clamp less a safety margin. Every section is
rendered first; sections that fit keep all they wrote, and the longest are cut
at a line boundary to one shared cap, which is never below an even fifth of
what the vintage header, the headings and the closing line leave. Every census
prints all its counts before any listing, so a cut drops listing rows unless a
section's counts alone outrun the cap, and a note marks where each cut falls.
Each census's timeout is what remains of a `--budget-seconds` budget less a
reserve for the censuses after it. The summary is rewritten after each census,
the sections so far held to their even share of the budget, so a later stop
keeps the earlier ones under the clamp; after the last census it is rewritten
once more under the whole budget, with the closing line.

The withheld-petitioner census always runs with `--no-listings`: its fill
needs only the summary counts, and its per-docket listing would point at the
dockets of pseudonymous filers. The side-motion census runs with its listings
unless the wrapper is given `--no-listings`.

Counts and identifiers only: each census holds to that, and the wrapper adds
nothing read from the corpus but the vintage.

Outside the lane, point `CHECK_SUMMARY` at any file and run it from a checkout
with a pulled corpus.
"""

from __future__ import annotations

import argparse
import contextlib
import os
import signal
import subprocess
import sys
import tempfile
import time
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from fedcourtsai.config import get_settings
from fedcourtsai.ids import parse_run_id

HERE = Path(__file__).resolve().parent

#: Under the lane's 30-minute check timeout, with room to write the summary.
DEFAULT_BUDGET_SECONDS = 27 * 60
#: Held back for each census still to run when the one before it is timed.
RESERVE_SECONDS = 120
#: The lane's clamp on the posted summary (docs/corpus-check.md).
LANE_LIMIT_BYTES = 50_000
#: Held back from the clamp for the lane's rewriting (redaction can lengthen a line).
SAFETY_MARGIN_BYTES = 2_000
DEFAULT_MAX_BYTES = LANE_LIMIT_BYTES - SAFETY_MARGIN_BYTES
#: How long the top-level `corpus-info` read may take.
CORPUS_INFO_TIMEOUT_SECONDS = 300

INFO_HEADER = "`fedcourts corpus-info`:\n\n"


@dataclass(frozen=True)
class Census:
    script: str
    entry: str
    placeholder: str
    #: ``always`` passes `--no-listings` every run, ``on-request`` only under the
    #: wrapper's own `--no-listings`, ``unsupported`` never.
    no_listings: Literal["always", "on-request", "unsupported"] = "unsupported"


CENSUSES: tuple[Census, ...] = (
    Census(
        "withheld_petitioner_census.py",
        "A Court docket that withholds the petitioner's counsel block is read as "
        + "self-represented (2026-10-15)",
        "census summary counts, blob sha and vintage",
        no_listings="always",
    ),
    Census(
        "side_motion_census.py",
        "An order on a side motion, in a closed list of shapes, no longer reads as an "
        + "interim disposal (2026-10-15)",
        "resolved-application census: pass 2",
        no_listings="on-request",
    ),
    Census(
        "post_conference_census.py",
        "A forward cell the record cannot show to be forward is set aside (2026-10-16)",
        "post-conference census at the carrying head",
    ),
    Census(
        "increment_timing_census.py",
        "An increment claim whose signal was on the docket before its forward cell "
        + "ran is masked (2026-10-16)",
        "increment timing census at the PR head",
    ),
    Census(
        "interim_partial_moot_census.py",
        "A finer, descriptive reading of interim partial grants and moot dismissals "
        + "(2026-10-16)",
        "interim reading census",
    ),
)


def cut_note(kept: int, total: int) -> str:
    return (
        "\n[section cut at a line boundary to keep the summary within its byte budget "
        + f"(the lane clamps it at {LANE_LIMIT_BYTES:,}): {kept:,} of {total:,} bytes kept; "
        + "the lines after this point are dropped]\n"
    )


def clamp(text: str, limit: int) -> str:
    """``text`` cut at a line boundary to at most ``limit`` UTF-8 bytes, note included."""
    encoded = text.encode("utf-8")
    if len(encoded) <= limit:
        return text
    room = limit - len(cut_note(len(encoded), len(encoded)).encode("utf-8"))
    kept: list[str] = []
    used = 0
    for line in text.splitlines(keepends=True):
        size = len(line.encode("utf-8"))
        if used + size > room:
            break
        kept.append(line)
        used += size
    return "".join(kept) + cut_note(used, len(encoded))


def shared_cap(sizes: Sequence[int], budget: int) -> int:
    """The largest cap with ``sum(min(size, cap)) <= budget``: short sizes give their room up.

    Never below ``budget // len(sizes)``, since each size under its even share
    leaves the rest a larger one.
    """
    remaining = max(budget, 0)
    ordered = sorted(sizes)
    for index, size in enumerate(ordered):
        share = remaining // (len(ordered) - index)
        if size > share:
            return share
        remaining -= size
    return max(ordered, default=0)


def fit(sections: Sequence[str], budget: int) -> list[str]:
    """``sections``, the longest cut to one shared cap so that together they fit ``budget``."""
    cap = shared_cap([len(text.encode("utf-8")) for text in sections], budget)
    return [clamp(text, cap) for text in sections]


def run_one(census: Census, *, listings: bool, timeout: float) -> tuple[str, str | None]:
    """One census's summary text, and why it failed (``None`` when it did not)."""
    with tempfile.TemporaryDirectory(prefix="census-") as scratch:
        summary = Path(scratch) / "summary.md"
        summary.touch()
        argv = [sys.executable, str(HERE / census.script)]
        if not listings:
            argv.append("--no-listings")
        env = {**os.environ, "CHECK_SUMMARY": str(summary)}
        # Its own session, so a timeout stops the census's own subprocesses too.
        process = subprocess.Popen(argv, env=env, start_new_session=True)
        failure: str | None = None
        try:
            code = process.wait(timeout=max(timeout, 1.0))
            if code != 0:
                failure = f"exit {code}"
        except subprocess.TimeoutExpired:
            with contextlib.suppress(ProcessLookupError):
                os.killpg(process.pid, signal.SIGKILL)
            process.wait()
            failure = f"timed out after {int(timeout)} s"
        text = summary.read_text(encoding="utf-8")
    if not text.strip() and failure is None:
        failure = "wrote no summary"
    return text, failure


def corpus_info() -> tuple[str, str | None]:
    """`fedcourts corpus-info`'s output, and why it failed (``None`` when it did not)."""
    try:
        run = subprocess.run(
            [sys.executable, "-m", "fedcourtsai.cli", "corpus-info"],
            capture_output=True,
            text=True,
            check=False,
            timeout=CORPUS_INFO_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return "", f"timed out after {CORPUS_INFO_TIMEOUT_SECONDS} s"
    sys.stderr.write(run.stderr)
    if run.returncode != 0:
        return run.stdout, f"exit {run.returncode}"
    # It exits 0 on a missing local blob, which no census can read.
    if any(line.startswith("No corpus at") for line in run.stdout.splitlines()):
        return run.stdout, "no corpus"
    return run.stdout, None


def ledger_vintage(data_root: Path) -> str:
    """The newest prediction and evaluation run ids under ``data_root``'s cases."""
    cases = data_root / "cases"
    newest: dict[str, str] = {}
    for kind, artifact in (("predictions", "prediction.json"), ("evaluations", "evaluation.json")):
        # The run id is the artifact's own directory, however deep the lane nests it.
        runs = set()
        for path in cases.glob(f"*/*/events/*/{kind}/**/{artifact}"):
            try:
                parse_run_id(path.parent.name)
            except ValueError:
                continue
            runs.add(path.parent.name)
        newest[kind] = max(runs) if runs else "none"
    return (
        f"ledger read by the censuses: `{data_root}` at the checkout, newest prediction run "
        + f"{newest['predictions']}, newest evaluation run {newest['evaluations']}"
    )


def heading(census: Census, failure: str | None) -> str:
    """A census's section heading and status line."""
    return (
        f"\n## {census.entry}\n\n"
        + f"Fills: {census.placeholder}. Script: `scripts/checks/{census.script}`"
        + f"; {'FAILED, ' + failure if failure else 'ok'}.\n\n"
    )


def render(
    header: str, heads: Sequence[str], bodies: Sequence[str], closing: str, budget: int
) -> str:
    """The whole summary, its section bodies cut to share what the rest leaves of ``budget``."""
    fixed = "".join([header, *heads, closing])
    room = budget - len(fixed.encode("utf-8"))
    cut = fit(bodies, room)
    return header + "".join(h + b for h, b in zip(heads, cut, strict=True)) + closing


def footer(failed: Sequence[str]) -> str:
    if failed:
        return f"\nFailed: {'; '.join(failed)}.\n"
    return f"\nAll {len(CENSUSES)} censuses ran.\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument("--no-listings", action="store_true")
    parser.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
    parser.add_argument("--budget-seconds", type=float, default=DEFAULT_BUDGET_SECONDS)
    args = parser.parse_args(argv)
    summary = os.environ.get("CHECK_SUMMARY")
    if not summary:
        print("CHECK_SUMMARY is unset; name the file to report to", file=sys.stderr)
        return 2
    out = Path(summary)
    # What the file held before this run is left alone; only this run's text is rewritten.
    offset = out.stat().st_size if out.exists() else 0
    started = time.monotonic()
    info, info_failure = corpus_info()
    data_root = get_settings().data_root
    header = (
        "Freeze-record census fills.\n\n"
        + INFO_HEADER
        + info
        + "\n"
        + ledger_vintage(data_root)
        + "\n"
    )
    failed: list[str] = []
    if info_failure is not None:
        failed.append(f"corpus-info ({info_failure})")
    heads: list[str] = []
    bodies: list[str] = []

    def write(text: str) -> None:
        with out.open("r+b" if out.exists() else "wb") as handle:
            handle.seek(offset)
            handle.truncate()
            handle.write(text.encode("utf-8"))

    for index, census in enumerate(CENSUSES):
        left_after = len(CENSUSES) - index - 1
        remaining = args.budget_seconds - (time.monotonic() - started)
        timeout = remaining - RESERVE_SECONDS * left_after
        text: str
        failure: str | None
        if timeout <= 0:
            text, failure = "", "not run: the time budget was spent"
        else:
            listings = census.no_listings == "unsupported" or (
                census.no_listings == "on-request" and not args.no_listings
            )
            text, failure = run_one(census, listings=listings, timeout=timeout)
        if info and INFO_HEADER + info in text:
            text = text.replace(INFO_HEADER + info, "`fedcourts corpus-info`: as at the top.\n")
        if failure is not None:
            failed.append(f"{census.script} ({failure})")
        heads.append(heading(census, failure))
        bodies.append(text)
        # Written now, so a stop keeps it: the sections so far share their even
        # part of the budget, leaving the sections still to come theirs.
        share = args.max_bytes * len(bodies) // len(CENSUSES)
        write(render(header, heads, bodies, "", share))
    write(render(header, heads, bodies, footer(failed), args.max_bytes))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
