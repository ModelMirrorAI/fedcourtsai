# Retrieval log

## Corpus tooling

- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
  stderr: `ranged corpus reads: 27 GET(s), 6946816 byte(s)`
  Returned recent grants and substantive applications (Marschner, Rhoney, DHS v. D.V.D., etc.); none is a qualified-immunity prior, so they did not shape the number.
- `uv run fedcourts query --court scotus --era 2020s --limit 8`
  stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm service cache)
  Returned petitions distributed for the 9/28/2026 conference and denied on 10/5/2026 — used only to confirm the Court was clearing the long conference on Oct. 5, which makes this docket's Oct. 5 redistribution a true relist.
- `uv run fedcourts open-events --court scotus` piped through a grep for Bossier / Hershey: no match (no transfer line is printed by `open-events`). The City's cross-petition No. 25-1323 is not an open event in the corpus.
- Base rates: the committed `metrics/statpack.md` — "Modern discretionary-cert petitions by disposition", "Modern cert petitions by originating circuit", "Cert petitions by relist count (paid scored segment)", "Cert petitions by CVSG status (paid scored segment)", "Cert petitions by salience band", and "Segment base rate by salience band (sal-v4)" (elevated `reached` pooled over Terms 2017–2024: 17.2%, n = 2810).

## CourtListener MCP (forward mode, 2 calls)

1. `search` dockets, court scotus, docket number `25-1323`: no results.
2. `search` dockets, court scotus, case name "Bossier City", filed after 2026-01-01: no results.

No web searches. Nothing retrieved concerned this petition's own disposition.
