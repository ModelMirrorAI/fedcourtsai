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

A census that fails, times out or writes nothing is reported under its heading
and the rest still run; the wrapper exits non-zero naming each one that
failed. The lane posts the summary as a PR comment clamped to 50,000 bytes and
stops a check at 30 minutes (docs/corpus-check.md), so each section is cut at
a line boundary to `--max-section-bytes` (counts lead every section, so a cut
drops listing rows only), each census's timeout is what remains of a
`--budget-seconds` budget less a reserve for the censuses after it, and the
summary is written after each census, so a later stop keeps the earlier ones.
`--no-listings` is passed to the two censuses that take it.

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

from fedcourtsai.config import get_settings
from fedcourtsai.ids import parse_run_id

HERE = Path(__file__).resolve().parent

#: Under the lane's 30-minute check timeout, with room to write the summary.
DEFAULT_BUDGET_SECONDS = 27 * 60
#: Held back for each census still to run when the one before it is timed.
RESERVE_SECONDS = 120
#: Five sections and the header under the lane's 50,000-byte clamp.
DEFAULT_MAX_SECTION_BYTES = 9_000

INFO_HEADER = "`fedcourts corpus-info`:\n\n"


@dataclass(frozen=True)
class Census:
    script: str
    entry: str
    placeholder: str
    takes_listings_flag: bool = False


CENSUSES: tuple[Census, ...] = (
    Census(
        "withheld_petitioner_census.py",
        "A Court docket that withholds the petitioner's counsel block is read as "
        + "self-represented (2026-10-15)",
        "census summary counts, blob sha and vintage",
        takes_listings_flag=True,
    ),
    Census(
        "side_motion_census.py",
        "An order on a side motion, in a closed list of shapes, no longer reads as an "
        + "interim disposal (2026-10-15)",
        "resolved-application census: pass 2",
        takes_listings_flag=True,
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


def clamp(text: str, limit: int) -> str:
    """``text`` cut at a line boundary to ``limit`` UTF-8 bytes, saying so when cut."""
    encoded = text.encode("utf-8")
    if len(encoded) <= limit:
        return text
    kept: list[str] = []
    used = 0
    for line in text.splitlines(keepends=True):
        size = len(line.encode("utf-8"))
        if used + size > limit:
            break
        kept.append(line)
        used += size
    return "".join(kept) + (
        f"\n[section cut at {used} of {len(encoded)} bytes; the counts lead the section, "
        + "so only listing rows are dropped]\n"
    )


def run_one(census: Census, *, listings: bool, timeout: float) -> tuple[str, str | None]:
    """One census's summary text, and why it failed (``None`` when it did not)."""
    with tempfile.TemporaryDirectory(prefix="census-") as scratch:
        summary = Path(scratch) / "summary.md"
        summary.touch()
        argv = [sys.executable, str(HERE / census.script)]
        if census.takes_listings_flag and not listings:
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


def corpus_info() -> tuple[str, int]:
    run = subprocess.run(
        [sys.executable, "-m", "fedcourtsai.cli", "corpus-info"],
        capture_output=True,
        text=True,
        check=False,
    )
    sys.stderr.write(run.stderr)
    return run.stdout, run.returncode


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


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument("--no-listings", action="store_true")
    parser.add_argument("--max-section-bytes", type=int, default=DEFAULT_MAX_SECTION_BYTES)
    parser.add_argument("--budget-seconds", type=int, default=DEFAULT_BUDGET_SECONDS)
    args = parser.parse_args(argv)
    summary = os.environ.get("CHECK_SUMMARY")
    if not summary:
        print("CHECK_SUMMARY is unset; name the file to report to", file=sys.stderr)
        return 2
    out = Path(summary)
    started = time.monotonic()
    info, info_code = corpus_info()
    data_root = get_settings().data_root
    with out.open("a", encoding="utf-8") as handle:
        handle.write("Freeze-record census fills.\n\n")
        handle.write(INFO_HEADER + info + "\n")
        handle.write(ledger_vintage(data_root) + "\n")
    failed: list[str] = []
    if info_code != 0:
        failed.append(f"corpus-info (exit {info_code})")
    for index, census in enumerate(CENSUSES):
        left_after = len(CENSUSES) - index - 1
        remaining = args.budget_seconds - (time.monotonic() - started)
        timeout = remaining - RESERVE_SECONDS * left_after
        text: str
        failure: str | None
        if timeout <= 0:
            text, failure = "", "not run: the time budget was spent"
        else:
            text, failure = run_one(census, listings=not args.no_listings, timeout=timeout)
        if info and INFO_HEADER + info in text:
            text = text.replace(INFO_HEADER + info, "`fedcourts corpus-info`: as at the top.\n")
        if failure is not None:
            failed.append(f"{census.script} ({failure})")
        with out.open("a", encoding="utf-8") as handle:
            handle.write(f"\n## {census.entry}\n\n")
            handle.write(f"Fills: {census.placeholder}. Script: `scripts/checks/{census.script}`")
            handle.write(f"; {'FAILED, ' + failure if failure else 'ok'}.\n\n")
            handle.write(clamp(text, args.max_section_bytes))
    with out.open("a", encoding="utf-8") as handle:
        if failed:
            handle.write(f"\nFailed: {'; '.join(failed)}.\n")
        else:
            handle.write("\nAll five censuses ran.\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
