# Retrieval log — scotus/73281057 / evt-petition-disposition / claude-baseline / 20260716T205846Z

Mode: `forward` (unrestricted retrieval; no disposition exists for this case —
the CVSG issued 2026-06-22 and the SG has not yet filed).

## Corpus lookups (`fedcourts` CLI, ranged reads against the remote corpus)

1. `uv run fedcourts query --court scotus --citation "467 U.S. 986" --citation "576 U.S. 350" --era 2020s`
   — `ranged corpus reads: 418 GET(s), 109576192 byte(s)` — no rows returned
   (no resolved 2020s SCOTUS priors indexed against the Ruckelshaus/Horne citations).
2. `uv run fedcourts query --court scotus --citation "447 U.S. 557" --citation "585 U.S. 755" --citation "463 U.S. 60"`
   — `ranged corpus reads: 418 GET(s), 109576192 byte(s)` — no rows returned.
3. `uv run fedcourts query --court scotus --topic "First Amendment"`
   — `ranged corpus reads: 3 GET(s), 786432 byte(s)` — no rows returned.
4. `uv run fedcourts query --court scotus --disposition granted --era 2020s`
   — `ranged corpus reads: 144 GET(s), 37748736 byte(s)` — returned recent
   granted priors (June 2026 grants); used only as general context on current
   grant patterns; no close analog to this case surfaced.

## Base rates

- Committed `metrics/statpack.md`: modern discretionary-cert base rates,
  originating-circuit cut, relist cut, and the **CVSG cut** (granted 27.1% /
  denied 71.2%, n=59 resolved) — the primary anchor.
- Committed `metrics/statpack.json`: per-Term fee-class detail (Term 2025
  paid est. grant rate 5.4%). Note: no "Segment base rate by salience band"
  section exists in the committed statpack, so the CVSG/relist cuts were used
  directly.

## CourtListener MCP lookups

1. `search(type=o, q="drug price transparency" "First Amendment" compelled disclosure, filed_after=2020-01-01)`
   — 2 hits: the decision below (*PhRMA v. Stolfi*, 9th Cir. 24-1570,
   2025-08-26) and *Merck & Co. v. HHS*, 962 F.3d 531 (D.C. Cir. 2020) (the
   federal drug-price TV-ad disclosure rule, vacated on statutory grounds) —
   used as context on the federal government's own stake in disclosure
   mandates when weighing the likely SG recommendation. No search touched
   this case's disposition (none exists).

## Web searches

None.
