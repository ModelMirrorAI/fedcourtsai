"""Census the re-docketed SCOTUS numbers and what the detector refuses.

Declared in a pull request's description as

    ```corpus-check
    uv run python scripts/checks/redocketed_numbers.py
    ```

it runs over the corpus the lane pulled, the content store's dated snapshots
and the ledger at the checkout, and appends counts and case identifiers — never
stored snapshot text or a caption — to the file named by `CHECK_SUMMARY`. It
heads the summary with the corpus vintage, the ledger checkout's git HEAD and
the newest stored snapshot date it read.

1. **What the detector refuses today** (`pipeline.redocket.is_redocketed`):
   the SCOTUS corpus events with a title (and how many of them sit on a row
   with a caption, the only ones the rule can read), and every committed ledger
   `event.yaml`. For each population: how many carry a caption string unlike
   the row's current caption (mostly re-renderings of the same parties), how
   many differ in party words on either side (before the rule's respondent-side
   guards), and how many the rule refuses,
   split by whether a committed outcome and a committed prediction sit beside
   it.
2. **Re-docketed numbers in the snapshot record**: for every live-polled
   SCOTUS row of the named Term prefixes (default `26-`, `26A`, `25-`, `25A`)
   with two or more stored live snapshots, its earliest and latest snapshot
   compared on the docketed date, each caption side's party words and the
   lower-court case numbers. A row whose party words differ on either side is
   counted re-docketed — a wider definition than the rule, which reads an
   interim moment on the petitioner side alone and a respondent change only
   with a moved docketed date. A row whose docketed date alone moved is
   reported apart, as a date correction. Each row lists which fields changed
   and its ledger events with their prediction and outcome counts.
   Earliest-against-latest is a floor: a number re-entered and then restored
   reads as unchanged, and a row with one stored snapshot cannot be compared.
3. **Every predicted case**: every SCOTUS case holding a committed prediction,
   all its stored live snapshots compared pair by consecutive pair on the
   caption sides' party words; each case whose parties change lists the
   snapshot dates of the change and the prediction runs dated before it, and
   apart the runs dated the same day, which a date alone cannot place.

Outside the lane, point `CHECK_SUMMARY` at any file and run it from a checkout
with a pulled corpus and the content store addressed.
"""

from __future__ import annotations

import itertools
import json
import os
import subprocess
import sys
import threading
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path
from typing import Any

from fedcourtsai import casestore, corpus
from fedcourtsai.config import get_settings
from fedcourtsai.pipeline.redocket import (
    EventIdentity,
    caption_sides,
    is_redocketed,
    ledger_identities,
    party_words,
    sides_differ,
)

_PREFIXES = ("26-", "26A", "25-", "25A")
_WORKERS = 32


class _Newest:
    """The newest stored snapshot date any read touched."""

    def __init__(self) -> None:
        self.day: date | None = None
        self._lock = threading.Lock()

    def see(self, days: list[date]) -> None:
        if days:
            with self._lock:
                self.day = max(days) if self.day is None else max(self.day, *days)


_NEWEST = _Newest()


def _event_dir_counts(event_dir: Path) -> tuple[int, bool]:
    predictions = len(list(event_dir.glob("predictions/*/*/prediction.json")))
    return predictions, (event_dir / "outcome.json").is_file()


def _captions_differ(title: str, current: str) -> bool:
    event_sides, current_sides = caption_sides(title), caption_sides(current)
    return any(sides_differ(a, b) for a, b in zip(event_sides, current_sides, strict=True))


def _ledger_detail(data_root: Path, case_id: str) -> str:
    events = sorted((data_root / "cases" / case_id / "events").glob("*/event.yaml"))
    parts = []
    for path in events:
        predictions, outcome = _event_dir_counts(path.parent)
        parts.append(
            f"{path.parent.name} predictions {predictions} outcome {'yes' if outcome else 'no'}"
        )
    return "; ".join(parts) or "no ledger events"


def _refusals(db: Path, data_root: Path) -> list[str]:
    """Section 1: the events the detector refuses against today's rows."""
    lines: list[str] = []
    with corpus.connect_local_read(db) as conn:
        rows = {
            str(r[0]): (str(r[1] or ""), date.fromisoformat(r[2]) if r[2] else None)
            for r in conn.execute(
                "SELECT case_id, case_name, date_filed FROM cases WHERE court = 'scotus'"
            )
        }
        titled = compared = differ = string_differs = 0
        corpus_hits: list[str] = []
        for case_id, event_id, title, opened, stage in conn.execute(
            "SELECT case_id, event_id, title, opened_at, stage FROM events "
            "WHERE court = 'scotus' AND title != ''"
        ):
            titled += 1
            caption, docketed = rows.get(str(case_id), ("", None))
            if not caption:
                continue
            compared += 1
            string_differs += str(title) != caption
            differ += _captions_differ(str(title), caption)
            identity = EventIdentity(
                str(title), date.fromisoformat(opened) if opened else None, stage
            )
            if is_redocketed(identity, caption, docketed):
                corpus_hits.append(f"{case_id} {event_id}")
    lines.append(
        f"- corpus events with a title: {titled}; on a row with a caption: {compared} "
        f"(the rest sit on captionless rows the rule cannot read); caption string "
        f"differs: {string_differs}; party words differ on a side: {differ}; "
        f"refused: {len(corpus_hits)} "
        f"({', '.join(sorted(corpus_hits)) or '-'})"
    )
    ledger_compared = ledger_differ = ledger_string_differs = 0
    split: Counter[str] = Counter()
    ledger_hits: list[str] = []
    for case_dir in sorted((data_root / "cases" / "scotus").glob("*")):
        case_id = f"scotus/{case_dir.name}"
        caption, docketed = rows.get(case_id, ("", None))
        event_ids = [p.parent.name for p in case_dir.glob("events/*/event.yaml")]
        if not caption or not event_ids or not case_dir.name.isdigit():
            continue
        identities = ledger_identities(data_root, "scotus", int(case_dir.name), event_ids)
        for event_id, identity in sorted(identities.items()):
            ledger_compared += 1
            ledger_string_differs += identity.title != caption
            ledger_differ += _captions_differ(identity.title, caption)
            if not is_redocketed(identity, caption, docketed):
                continue
            predictions, outcome = _event_dir_counts(case_dir / "events" / event_id)
            split[f"outcome={outcome} predicted={predictions > 0}"] += 1
            ledger_hits.append(
                f"{case_id} {event_id} (predictions {predictions}, "
                f"outcome {'yes' if outcome else 'no'})"
            )
    lines.append(
        f"- ledger event.yaml compared: {ledger_compared}; caption string differs: "
        f"{ledger_string_differs}; party words differ on a side: {ledger_differ}; "
        f"refused: {len(ledger_hits)} "
        f"[{', '.join(f'{k}: {v}' for k, v in sorted(split.items())) or '-'}]"
    )
    lines.extend(f"  - {hit}" for hit in ledger_hits)
    return lines


def _sides(payload: dict[str, Any]) -> tuple[frozenset[str], frozenset[str]]:
    return (
        party_words(str(payload.get("PetitionerTitle") or "")),
        party_words(str(payload.get("RespondentTitle") or "")),
    )


def _compare(transport: casestore.ObjectTransport, case_id: str) -> tuple[str, dict[str, bool]]:
    """One row's earliest and latest live snapshot, compared on its identity fields."""
    dates = sorted(casestore._snapshot_dates(transport, case_id))
    _NEWEST.see(dates)
    if len(dates) < 2:
        return "single", {}
    bodies = [transport.get(casestore.snapshot_key(case_id, d)) for d in (dates[0], dates[-1])]
    first, last = (json.loads(b) if b else {} for b in bodies)
    if "CaseNumber" not in first or "CaseNumber" not in last:
        return "not-live", {}
    first_sides, last_sides = _sides(first), _sides(last)
    return "pair", {
        "docketed": first.get("DocketedDate") != last.get("DocketedDate"),
        "petitioner": sides_differ(first_sides[0], last_sides[0]),
        "respondent": sides_differ(first_sides[1], last_sides[1]),
        "lower": str(first.get("LowerCourtCaseNumbers") or "").strip()
        != str(last.get("LowerCourtCaseNumbers") or "").strip(),
    }


def _flags(found: dict[str, bool]) -> str:
    return ", ".join(k for k, v in found.items() if v) or "none"


def _snapshot_census(db: Path, data_root: Path, prefixes: list[str]) -> list[str]:
    """Section 2: re-docketed numbers read off the stored snapshots."""
    transport = casestore.active_transport()
    if transport is None:
        return ["- content store not addressed; section skipped"]
    with corpus.connect_local_read(db) as conn:
        case_ids = [
            str(r[0])
            for prefix in prefixes
            for r in conn.execute(
                "SELECT case_id FROM cases WHERE court = 'scotus' AND docket_number LIKE ? "
                "AND last_live_polled IS NOT NULL",
                (prefix + "%",),
            )
        ]
        numbers = {
            str(r[0]): str(r[1])
            for r in conn.execute("SELECT case_id, docket_number FROM cases WHERE court = 'scotus'")
        }
    with ThreadPoolExecutor(_WORKERS) as pool:
        results = list(pool.map(lambda cid: (cid, *_compare(transport, cid)), case_ids))
    kinds = Counter(kind for _, kind, _ in results)
    found = {cid: f for cid, kind, f in results if kind == "pair"}
    redocketed = sorted(c for c, f in found.items() if f["petitioner"] or f["respondent"])
    date_only = sorted(
        c for c, f in found.items() if f["docketed"] and not (f["petitioner"] or f["respondent"])
    )
    flags = Counter(k for f in found.values() for k, v in f.items() if v)
    lines = [
        f"- prefixes {', '.join(prefixes)}: {len(case_ids)} live-polled rows; "
        + ", ".join(f"{k} {v}" for k, v in sorted(kinds.items())),
        "- changed between earliest and latest snapshot: "
        + (", ".join(f"{k} {v}" for k, v in sorted(flags.items())) or "none"),
        f"- re-docketed (a caption side's party words differ): {len(redocketed)}",
    ]
    lines.extend(
        f"  - {cid} ({numbers.get(cid, '?')}): changed {_flags(found[cid])}; "
        f"{_ledger_detail(data_root, cid)}"
        for cid in redocketed
    )
    lines.append(
        f"- docketed date moved, same parties (date correction, not refused): {len(date_only)}"
    )
    lines.extend(
        f"  - {cid} ({numbers.get(cid, '?')}): changed {_flags(found[cid])}; "
        f"{_ledger_detail(data_root, cid)}"
        for cid in date_only
    )
    return lines


def _party_changes(transport: casestore.ObjectTransport, case_id: str) -> tuple[str, list[str]]:
    """Every stored live snapshot of a case, consecutive pairs compared on party words.

    Returns the case's kind (``single``, ``compared``) and the dates of the
    snapshots that first show other parties than the one before.
    """
    dates = sorted(casestore._snapshot_dates(transport, case_id))
    _NEWEST.see(dates)
    sides: list[tuple[str, tuple[frozenset[str], frozenset[str]]]] = []
    for day in dates:
        body = transport.get(casestore.snapshot_key(case_id, day))
        payload = json.loads(body) if body else {}
        if "CaseNumber" in payload:
            sides.append((day.isoformat(), _sides(payload)))
    if len(sides) < 2:
        return "single", []
    return "compared", [
        day
        for (_, before), (day, after) in itertools.pairwise(sides)
        if sides_differ(before[0], after[0]) or sides_differ(before[1], after[1])
    ]


def _predicted_census(data_root: Path) -> list[str]:
    """Section 3: every SCOTUS case holding a committed prediction, every snapshot pair."""
    transport = casestore.active_transport()
    if transport is None:
        return ["- content store not addressed; section skipped"]
    runs: dict[str, set[str]] = {}
    for path in (data_root / "cases" / "scotus").glob("*/events/*/predictions/*/*/prediction.json"):
        runs.setdefault(f"scotus/{path.parents[5].name}", set()).add(path.parent.name)
    with ThreadPoolExecutor(_WORKERS) as pool:
        results = list(pool.map(lambda cid: (cid, *_party_changes(transport, cid)), sorted(runs)))
    kinds = Counter(kind for _, kind, _ in results)
    lines = [
        f"- cases with a committed prediction: {len(runs)}; "
        + ", ".join(f"{k} {v}" for k, v in sorted(kinds.items())),
        f"- party change between consecutive snapshots: "
        f"{sum(1 for _, _, changes in results if changes)}",
    ]
    for cid, _, changes in results:
        if not changes:
            continue
        day = changes[0].replace("-", "")
        before = sorted(r for r in runs[cid] if r[:8] < day)
        same_day = sorted(r for r in runs[cid] if r[:8] == day)
        lines.append(
            f"  - {cid}: parties change at snapshot {', '.join(changes)}; "
            f"prediction runs before it: {', '.join(before) or 'none'}; "
            f"runs the same day (unplaced): {', '.join(same_day) or 'none'}"
        )
    return lines


def _git_head(path: Path) -> str:
    head = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--short", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    return head.stdout.strip() or "unknown"


def main() -> int:
    summary = os.environ.get("CHECK_SUMMARY")
    if not summary:
        print("CHECK_SUMMARY is unset; name the file to report to", file=sys.stderr)
        return 2
    settings = get_settings()
    db = corpus.corpus_db_path(settings.corpus_root)
    if not db.exists():
        print(f"no corpus at {db}; corpus-pull first", file=sys.stderr)
        return 1
    info = subprocess.run(
        [sys.executable, "-m", "fedcourtsai.cli", "corpus-info"],
        capture_output=True,
        text=True,
        check=False,
    )
    prefixes = sys.argv[1:] or list(_PREFIXES)
    body = ["", "**1. What the detector refuses today**", ""]
    body += _refusals(db, settings.data_root)
    body += ["", "**2. Re-docketed numbers in the snapshot record**", ""]
    body += _snapshot_census(db, settings.data_root, prefixes)
    body += ["", "**3. Every predicted case, every snapshot pair**", ""]
    body += _predicted_census(settings.data_root)
    lines = ["### Re-docketed SCOTUS numbers", "", "`fedcourts corpus-info`:", ""]
    lines += [f"    {line}" for line in info.stdout.splitlines()]
    lines += [
        "",
        f"- ledger checkout HEAD: `{_git_head(settings.data_root)}`",
        f"- newest stored snapshot date read: {_NEWEST.day or 'none'}",
    ]
    lines += body
    with Path(summary).open("a", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
