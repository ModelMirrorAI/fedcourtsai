# Retrieval log — scotus/73280982 evt-petition-disposition (claude-baseline, 20260716T205846Z)

## Corpus base rates

- Read the committed `metrics/statpack.md`: modern discretionary-cert
  disposition table, originating-circuit cut, relist cut, and the **CVSG cut**
  (cvsg: denied 71.2%, granted 27.1%, dismissed 1.7% over 59 resolved) — the
  primary quantitative anchor. This statpack version carries no per-Term
  salience-band table.

## Corpus lookups (`fedcourts query`, ranged backend)

1. `uv run fedcourts query --court scotus --era 2020s --citation "15 U.S.C. 77k" --limit 8`
   → 0 rows. `ranged corpus reads: 418 GET(s), 109576192 byte(s)`
2. `uv run fedcourts query --court scotus --era 2020s --topic securities --limit 8`
   → 0 rows. `ranged corpus reads: 3 GET(s), 786432 byte(s)`
3. `uv run fedcourts query --court scotus --citation "77k" --limit 8`
   → 0 rows. `ranged corpus reads: 418 GET(s), 109576192 byte(s)`
4. `uv run fedcourts query --court scotus --era 2020s --limit 5`
   → 5 rows (recent resolved cert petitions; none securities-specific, used
   only as a sanity check on corpus row shape). `ranged corpus reads: 418 GET(s), 109576192 byte(s)`

No citation- or topic-indexed securities priors surfaced, so the qualitative
prior work rests on the provisioned petition/BIO and general legal knowledge
(*Macquarie v. Moab*, *Slack v. Pirani*, the OT2024 NVIDIA/Facebook DIGs).

## CourtListener MCP

None. The provisioned snapshot (2026-07-16, current through the June 1, 2026
CVSG) plus the provisioned petition and brief-in-opposition texts were
sufficient; no MCP lookups were made.

## Web searches

None.
