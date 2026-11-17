# Evaluator Retrieval Log

## Corpus Lookups (`fedcourts query`)

1. `uv run fedcourts query --court scotus --docket-number "26-80" --full`
   - Transfer line: `ranged corpus reads: 21 GET(s), 5505024 byte(s)`
   - Purpose: Verified `gemini-baseline`'s factual reference to Petitioner's prior related certiorari petition (`scotus/9026000080`, *Felicia Scroggins v. City of Shreveport, Louisiana*, No. 26-80, arising from CA5 No. 24-30777, filed `2026-07-17`, distributed once on `2026-09-28`, denied `2026-10-05`).

## Statpack History Verification

- Inspected committed `metrics/statpack.md` (`sal-v8`) alongside `git show 1913c7a1172a0e3316053811b8b2de54525963d8:metrics/statpack.md` (`sal-v4`, the statpack build in force at the candidates' `2026-10-31T01:03:06Z` prediction run, matching their `cert_anchor.statpack_digest = sha256:063aea1961d5833e02e3aa0254477260a34f98f23a2751a1620aaf7c8db03726`) to verify all candidate-cited base-rate figures and denominators against the pack they read.

## CourtListener MCP and Web Lookups

- No CourtListener MCP calls.
- No web searches.
