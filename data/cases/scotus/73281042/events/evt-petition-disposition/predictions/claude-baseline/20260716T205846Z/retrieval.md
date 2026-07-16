# Retrieval log — scotus/73281042 · evt-petition-disposition · claude-baseline · 20260716T205846Z

Mode: `forward` (pending petition; CVSG outstanding). Retrieval was kept
minimal because the provisioned snapshot was fetched the same day as this run
(2026-07-16) and the provisioned petition/BIO texts already survey the
surrounding litigation landscape as of May–June 2026.

## Corpus lookups (`fedcourts`, ranged backend)

1. `uv run fedcourts query --court scotus --topic "First Amendment expressive association antidiscrimination" --limit 5`
   → 0 rows; stderr: `ranged corpus reads: 3 GET(s), 786432 byte(s)`
2. `uv run fedcourts query --court scotus --topic "bar association discrimination" --limit 5`
   → 0 rows; stderr: `ranged corpus reads: 3 GET(s), 786432 byte(s)`
3. `uv run fedcourts query --court scotus --topic "First Amendment" --limit 5`
   → 0 rows; stderr: `ranged corpus reads: 3 GET(s), 786432 byte(s)`
4. `uv run fedcourts query --court scotus --topic discrimination --limit 8`
   → 0 rows; stderr: `ranged corpus reads: 3 GET(s), 786432 byte(s)`
5. `uv run fedcourts open-events --court scotus --docket 73281042`
   → `evt-petition-disposition` (confirms the predicted event is open; no
   ranged-read stderr line was emitted by this invocation)

No topic query returned priors, so no retrieved corpus priors informed the
prediction; base-rate context came from the committed `metrics/statpack.md`
and `metrics/statpack.json` (CVSG cut, relist cut, per-Term paid/IFP grant
rates), which are repo files, not retrieval.

## CourtListener MCP lookups

None. The snapshot was fetched on the run date and includes the latest docket
entry (June 22, 2026 CVSG); no fresher docket state was needed, and this
case's own outcome does not yet exist.

## Web searches

None.
