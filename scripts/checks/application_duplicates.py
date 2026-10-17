"""Census the SCOTUS application numbers the corpus stores as more than one row.

Declared in a pull request's description as

    ```corpus-check
    uv run python scripts/checks/application_duplicates.py
    ```

it runs over the corpus the lane pulled and the ledger at the checkout, and
appends counts, case identifiers, field names and disposition labels — never
stored snapshot text or a caption — to the file named by `CHECK_SUMMARY`. It
heads the summary with the corpus vintage and the ledger checkout's git HEAD.

1. **The groups.** Every strict-form (`YYAnnn`) application number held under
   two or more case ids, keyed as the statpack keys it
   (:func:`fedcourtsai.corpus.duplicate_application_case_ids`): per Term, the
   number of duplicated numbers and the extra rows; per group, its case ids
   with the counted survivor first, whether any id sits in the live-minted
   reserved range, live-slice membership, how many rows the live channel
   observed (parsed or live-polled), the parsed ask, the disposition, and the
   names of the fields the rows disagree on; then the groups mixing observed
   and unobserved rows, any group counting an unobserved row over an observed
   one (the survivor rule makes this zero), and the groups whose counted row is
   not the plain lowest docket id.
2. **What each reader double-counts.** The statpack's interim per-Term counts
   with every row (the rule before the dedupe) and with one row per number
   (the rule after), with the rows' difference by field; the pooled interim
   base rate (`pipeline.base_rates.interim_base_rate`, at the configured
   `salience.base_rate_lookback_terms`) for each application Term the pool
   reaches, before and after; and a cross-check that the after counts equal
   `build_statpack`'s own interim section.
3. **The other readers.** Whether `party-rates`' own first-row-per-docket
   survivor (live slice, `case_id` order) is the counted survivor in every
   group it sees; how many skipped rows carry a corpus event or a committed
   ledger directory; and, for context, the live-slice non-application numbers
   held under two ids, which are the `dedupe-live-rows` pass's population and
   not this rule's.

Outside the lane, point `CHECK_SUMMARY` at any file and run it from a checkout
with a pulled corpus.
"""

from __future__ import annotations

import os
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

from fedcourtsai import analytics, corpus
from fedcourtsai.config import get_settings, load_salience_config
from fedcourtsai.pipeline.base_rates import interim_base_rate
from fedcourtsai.schemas import StatPack
from fedcourtsai.supremecourt import is_live_docket_id, parse_scotus_application_number

_COUNT_FIELDS = (
    "applications",
    "extension",
    "substantive",
    "unknown",
    "unparsed",
    "substantive_resolved",
    "substantive_granted",
    "response_requested",
    "referred_to_court",
    "with_amicus",
    "duplicate_rows",
)


def _git_head(path: Path) -> str:
    head = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--short", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    return head.stdout.strip() or "unknown"


def _application_rows(conn: corpus.ReadConnection) -> list[corpus.CorpusRow]:
    return [
        row
        for row in corpus.iter_rows(conn, court="scotus")
        if corpus.scotus_application_term_year(row.docket_number) is not None
    ]


def _key(row: corpus.CorpusRow) -> tuple[int, int]:
    parsed = parse_scotus_application_number(corpus.strip_docket_annotation(row.docket_number))
    assert parsed is not None  # only application rows reach here
    return parsed


def _number(key: tuple[int, int]) -> str:
    return f"{key[0]:02d}A{key[1]}"


def _is_live_minted(case_id: str) -> bool:
    tail = case_id.rsplit("/", 1)[-1]
    return tail.isdigit() and is_live_docket_id(int(tail))


def _differing_fields(rows: list[corpus.CorpusRow]) -> list[str]:
    return [
        name
        for name in corpus.CorpusRow.model_fields
        if name != "case_id" and len({repr(getattr(row, name)) for row in rows}) > 1
    ]


def _interim(
    rows: list[corpus.CorpusRow], skipped: frozenset[str]
) -> dict[int, analytics._InterimAcc]:
    """The interim accumulators over ``rows``, tallying ``skipped`` as duplicates."""
    accs: dict[int, analytics._InterimAcc] = {}
    for row in rows:
        year = corpus.scotus_application_term_year(row.docket_number)
        assert year is not None
        acc = accs.setdefault(year, analytics._InterimAcc())
        if row.case_id in skipped:
            acc.skip_duplicate()
        else:
            acc.add(row)
    return accs


def _observed(row: corpus.CorpusRow) -> bool:
    """Whether the live channel observed the row: application-parsed or live-polled."""
    return row.application_kind is not None or row.last_live_polled is not None


def _lowest_id(case_id: str) -> tuple[int, int, str]:
    tail = case_id.rsplit("/", 1)[-1]
    return (0, int(tail), case_id) if tail.isdigit() else (1, 0, case_id)


def _pool(rate: float | None, pack: StatPack, term: int, lookback: int) -> str:
    assert pack.interim is not None
    oldest = term - lookback if lookback > 0 else None
    granted = resolved = 0
    for entry in pack.interim.terms:
        if entry.term >= term or (oldest is not None and entry.term < oldest):
            continue
        granted += entry.substantive_granted
        resolved += entry.substantive_resolved
    shown = f"{rate:.4f}" if rate is not None else "none (below the floor)"
    return f"{granted}/{resolved} = {shown}"


def _census(db: Path, data_root: Path, lookback: int) -> list[str]:  # noqa: PLR0915 - one report
    with corpus.connect_local_read(db) as conn:
        twins = corpus.duplicate_application_case_ids(conn)
        rows = _application_rows(conn)
        twin_events = {
            str(record["case_id"])
            for record in conn.execute("SELECT DISTINCT case_id FROM events")
            if str(record["case_id"]) in twins
        }
        live_other = conn.execute(
            "SELECT norm_dn(docket_number) AS dn, COUNT(*) AS n FROM cases "
            f"WHERE court = 'scotus' AND {corpus.LIVE_SLICE_SQL} "
            "AND norm_dn(docket_number) IS NOT NULL "
            "GROUP BY dn HAVING COUNT(*) > 1"
        ).fetchall()
    groups: dict[tuple[int, int], list[corpus.CorpusRow]] = defaultdict(list)
    for row in rows:
        groups[_key(row)].append(row)
    dup = {key: group for key, group in groups.items() if len(group) > 1}
    lines = ["**1. The groups**", ""]
    if not rows:
        return [*lines, "- the corpus holds no strict-form application rows"]
    lines.append(
        f"- application rows: {len(rows)}; numbers: {len(groups)}; duplicated numbers: "
        f"{len(dup)}; rows the dedupe skips: {len(twins)} "
        f"(group sizes {dict(sorted(Counter(len(g) for g in dup.values()).items()))})"
    )
    by_term: dict[int, list[int]] = defaultdict(lambda: [0, 0])
    for key, group in dup.items():
        year = corpus.scotus_application_term_year(_number(key))
        assert year is not None
        by_term[year][0] += 1
        by_term[year][1] += len(group) - 1
    lines.append(
        "- by Term (numbers, extra rows): "
        + ", ".join(f"OT{year} {n} / {extra}" for year, (n, extra) in sorted(by_term.items()))
    )
    lines.append("")
    lines.append(
        "| number | case ids (counted first) | live-minted | live slice | observed | ask | "
        "disposition | differing fields |"
    )
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for key in sorted(dup):
        group = sorted(dup[key], key=lambda row: row.case_id in twins)
        lines.append(
            f"| {_number(key)} | {', '.join(row.case_id for row in group)} | "
            f"{sum(_is_live_minted(row.case_id) for row in group)} | "
            f"{sum(corpus.is_live_slice(row) for row in group)} | "
            f"{sum(_observed(row) for row in group)} | "
            f"{'/'.join(sorted({str(row.application_kind) for row in group}))} | "
            f"{'/'.join(sorted({str(row.disposition) for row in group}))} | "
            f"{', '.join(_differing_fields(group)) or 'none'} |"
        )
    mixed = [
        key
        for key, group in dup.items()
        if any(_observed(row) for row in group) and not all(_observed(row) for row in group)
    ]
    stub_kept = [
        key
        for key, group in dup.items()
        if any(_observed(row) for row in group if row.case_id in twins)
        and not any(_observed(row) for row in group if row.case_id not in twins)
    ]
    plain = sum(
        min((row.case_id for row in group), key=_lowest_id) in twins for group in dup.values()
    )
    lines.append("")
    lines.append(
        f"- groups mixing observed and unobserved rows: {len(mixed)} "
        f"({', '.join(_number(key) for key in sorted(mixed)) or 'none'}); groups counting an "
        f"unobserved row while skipping an observed one: {len(stub_kept)}; groups whose "
        f"counted row is not the plain lowest docket id: {plain}"
    )

    before_accs = _interim(rows, frozenset())
    after_accs = _interim(rows, twins)
    before = StatPack(interim=analytics._interim_section(before_accs))
    after = StatPack(interim=analytics._interim_section(after_accs))
    built = analytics.build_statpack(corpus_db_path=db).interim
    lines += ["", "**2. What each reader double-counts**", ""]
    lines.append(
        "- `build_statpack`'s interim section equals the one-row-per-number counts: "
        f"{built == after.interim}"
    )
    lines.append("- statpack interim counts, every row -> one row per number (Terms that move):")
    assert before.interim is not None and after.interim is not None
    after_terms = {entry.term: entry for entry in after.interim.terms}
    for entry in before.interim.terms:
        moved = [
            f"{name} {getattr(entry, name)} -> {getattr(after_terms[entry.term], name)}"
            for name in _COUNT_FIELDS
            if getattr(entry, name) != getattr(after_terms[entry.term], name)
        ]
        if moved:
            lines.append(f"  - OT{entry.term}: {'; '.join(moved)}")
    moved_pack = [
        f"{name} {getattr(before.interim, name)} -> {getattr(after.interim, name)}"
        for name in _COUNT_FIELDS
        if getattr(before.interim, name) != getattr(after.interim, name)
    ]
    lines.append(f"  - pack level: {'; '.join(moved_pack)}")
    lines.append(
        f"- pooled interim base rate (strictly prior Terms, lookback {lookback}), "
        "every row -> one row per number:"
    )
    newest = max(after_terms)
    for term in range(min(after_terms) + 1, newest + 2):
        old = interim_base_rate(term, before, lookback_terms=lookback)
        new = interim_base_rate(term, after, lookback_terms=lookback)
        old_pool = _pool(old, before, term, lookback)
        new_pool = _pool(new, after, term, lookback)
        if old_pool == new_pool and old is None:
            continue
        lines.append(f"  - OT{term} application cells: {old_pool} -> {new_pool}")

    lines += ["", "**3. The other readers**", ""]
    live_groups: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        if corpus.is_live_slice(row):
            live_groups[row.docket_number.strip().upper()].append(row.case_id)
    seen = [ids for ids in live_groups.values() if len(ids) > 1]
    agree = sum(sorted(ids)[0] not in twins for ids in seen)
    lines.append(
        f"- `party-rates` (live slice, first row in `case_id` order per docket number): "
        f"{len(seen)} duplicated application numbers in its population; its survivor is "
        f"the counted survivor in {agree} of {len(seen)}"
    )
    ledger = [case_id for case_id in sorted(twins) if (data_root / "cases" / case_id).is_dir()]
    lines.append(
        f"- skipped rows carrying a corpus event: {len(twin_events)} "
        f"({', '.join(sorted(twin_events)) or 'none'}); with a committed ledger "
        f"directory: {len(ledger)} ({', '.join(ledger) or 'none'})"
    )
    other = [
        record
        for record in live_other
        if corpus.scotus_application_term_year(str(record["dn"])) is None
    ]
    lines.append(
        f"- context, not this rule's: live-slice non-application numbers under two or "
        f"more ids: {len(other)} ({', '.join(sorted(str(r['dn']) for r in other)) or 'none'})"
    )
    return lines


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
    lookback = load_salience_config(settings.config_root).base_rate_lookback_terms
    lines = ["### SCOTUS application numbers stored as more than one row", ""]
    lines += ["`fedcourts corpus-info`:", ""]
    lines += [f"    {line}" for line in info.stdout.splitlines()]
    lines += ["", f"- ledger checkout HEAD: `{_git_head(settings.data_root)}`", ""]
    lines += _census(db, settings.data_root, lookback)
    with Path(summary).open("a", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")
    sys.stderr.write(info.stderr)
    # The vintage is what a figure is quoted beside: a corpus-info that failed
    # leaves the figures unanchored, so the check fails with it.
    return info.returncode


if __name__ == "__main__":
    sys.exit(main())
