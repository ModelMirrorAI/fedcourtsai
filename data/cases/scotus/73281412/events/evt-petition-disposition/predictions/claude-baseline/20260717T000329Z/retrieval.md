# Retrieval log — scotus/73281412 / evt-petition-disposition / claude-baseline / 20260717T000329Z

Beyond the provisioned inputs (snapshot 2026-07-16, questions-presented.txt,
petition.txt, brief-in-opposition.txt, documents.json), I consulted:

## Committed base rates

- `metrics/statpack.md` — modern discretionary-cert disposition, originating
  circuit (CA5: 4.8% granted), relist, CVSG, and per-Term tables.
- `metrics/statpack.json` — per-Term fee-class detail (Term 2025 paid est.
  grant rate 5.4%, Term 2024 paid 6.9%).

## Corpus lookups (`fedcourts query`, ranged backend)

All three returned zero matching rows; stderr transfer lines as printed:

1. `uv run fedcourts query --court scotus --citation "Bell v. Wolfish" --citation "Estelle v. Gamble" --limit 8`
   — `ranged corpus reads: 419 GET(s), 109707264 byte(s)` — 0 rows.
2. `uv run fedcourts query --court scotus --citation "441 U.S. 520" --citation "429 U.S. 97" --limit 8`
   — `ranged corpus reads: 419 GET(s), 109707264 byte(s)` — 0 rows.
3. `uv run fedcourts query --court scotus --topic "civil rights" --limit 6`
   — `ranged corpus reads: 3 GET(s), 786432 byte(s)` — 0 rows.

## CourtListener MCP

None — the provisioned record (petition, both-sided briefing, full docket
proceedings through the July 13, 2026 BIOs) was sufficient, and this case's
own disposition does not yet exist (forward cell).

## Web searches

None.
