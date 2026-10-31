"""Size what the first live salience pass under the active version would write.

Declared in a pull request's description as

    ```corpus-check
    uv run python scripts/checks/salience_activation_dry_run.py
    ```

it plans the live selection pass over the pulled corpus without writing — the
plan ``reconcile-salience-selection`` prints as a dry run — and appends to the
file named by ``CHECK_SUMMARY``: the rows it would newly latch, by pending
conference, beside the latches already standing in those conferences (a
cohort's capacity counts no existing latch, so a version change adds its own
top-N beside them once); and the in-scope rows the active segment refuses,
split by whether they are latched and by the version their stored stamp names
(the pass stamps each with the active version and no score). Then the corpus
vintage. Counts only, never stored text.

Outside the lane, point ``CHECK_SUMMARY`` at any file and run it from a
checkout with a pulled corpus.
"""

from __future__ import annotations

import os
import subprocess
import sys
from collections import Counter
from datetime import UTC, date, datetime
from pathlib import Path

from fedcourtsai import corpus
from fedcourtsai.config import get_settings, load_salience_config
from fedcourtsai.pipeline import salience


def render(db: Path, config_root: Path, as_of: date) -> list[str]:
    config = load_salience_config(config_root)
    with corpus.connect_readonly(db) as conn:
        (scores, to_select, eligible, conferences), _, refused = salience._planned_selection(
            conn, config, as_of=as_of
        )
        picked = set(to_select)
        refused_ids = set(refused)
        new_by_conf: Counter[str] = Counter()
        standing_by_conf: Counter[str] = Counter()
        refused_by: Counter[tuple[bool, str]] = Counter()
        for row in corpus.iter_rows(conn, court="scotus"):
            conf = row.distributed_for_conference
            pending = conf is not None and corpus.resolution_date(row) is None
            if row.case_id in picked:
                new_by_conf[conf.isoformat() if conf else "arrival or reserve"] += 1
            elif pending and row.salience_selected and conf is not None:
                standing_by_conf[conf.isoformat()] += 1
            if row.case_id in refused_ids:
                refused_by[(row.salience_selected, row.salience_version or "none")] += 1
    lines = [
        f"Salience pass dry run under `{salience.SALIENCE_VERSION}` as of {as_of}: "
        f"{eligible} eligible, {len(scores)} scored, {len(picked)} newly selected "
        f"across {conferences} conference(s).",
        "",
        "| conference | newly selected | already latched |",
        "| --- | --: | --: |",
    ]
    for key in sorted(set(new_by_conf) | set(standing_by_conf)):
        lines.append(f"| {key} | {new_by_conf[key]} | {standing_by_conf[key]} |")
    lines += [
        "",
        f"Rows the active segment refuses: {len(refused_ids)}.",
        "",
        "| latched | stored stamp | rows |",
        "| --- | --- | --: |",
    ]
    for (latched, stamp), n in sorted(refused_by.items()):
        lines.append(f"| {'yes' if latched else 'no'} | {stamp} | {n} |")
    return lines


def main() -> int:
    summary = os.environ.get("CHECK_SUMMARY")
    if not summary:
        print("CHECK_SUMMARY is unset; name the file to report to", file=sys.stderr)
        return 2
    settings = get_settings()
    db = corpus.corpus_db_path(settings.corpus_root)
    if not db.exists():
        print(f"no corpus at {db}", file=sys.stderr)
        return 1
    lines = render(db, settings.config_root, datetime.now(UTC).date())
    info = subprocess.run(
        [sys.executable, "-m", "fedcourtsai.cli", "corpus-info"],
        capture_output=True,
        text=True,
        check=False,
    )
    with Path(summary).open("a", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n\n`fedcourts corpus-info`:\n\n")
        handle.write(info.stdout)
    sys.stderr.write(info.stderr)
    return info.returncode


if __name__ == "__main__":
    sys.exit(main())
