# Retrieval log

## Corpus lookups (`fedcourts query`, via the cell's corpus service)
1. `uv run fedcourts query --court scotus --era 2020s --disposition granted`
   stderr: `ranged corpus reads: 47 GET(s), 12320768 byte(s)`
   Returned recent granted SCOTUS rows (mostly substantive applications and represented cert petitions such as Apple v. Epic Games, Chaney v. United States). Used only for the shape of what grants look like; no returned prior resembled a pro se ERISA benefits petition.
2. `uv run fedcourts query --court scotus --era 2020s`
   stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm cache)
   Returned recent resolved SCOTUS rows, largely applications; not informative for this cell.

## Committed base rates
- `metrics/statpack.md`: "Modern discretionary-cert petitions by disposition", "by originating circuit" (ca4 row), "by relist count (paid scored segment)", "by CVSG status (paid scored segment)", "by salience band", "SCOTUS cert petitions by Term", and "Segment base rate by salience band (sal-v4)" (anchor: `baseline` bracketed `reached` rate pooled over OT2017–OT2024).

## CourtListener MCP lookups
1. `search` (type `o`, court `ca4`, q `Gasper EIDP`): found cluster 10750028, *David Gasper v. EIDP, Inc.*, No. 24-1959, filed 2025-12-08, status Published, opinion id 11216613.
2. `read_document` (opinion 11216613, chunks 0–3 of 6): read the panel opinion through the resolution of the benefits claim (standard of review, QDRO interpretation under North Carolina law, footnote 5 forfeiture of the § 1056(d)(3)(C) argument).

No web searches. Nothing retrieved concerned this petition's own disposition; all material predates the snapshot or is the decision below.
