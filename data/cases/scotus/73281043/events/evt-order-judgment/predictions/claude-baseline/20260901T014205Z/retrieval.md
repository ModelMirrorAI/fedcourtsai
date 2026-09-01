# Retrieval log

Beyond the provisioned inputs (snapshot 2026-06-16, event.yaml, context.json,
petition.txt, brief-in-opposition.txt, questions-presented.txt,
documents.json), I consulted:

## Committed base rates

- `metrics/statpack.md`, "The merits docket (granted cases)" section — pooled
  the per-Term disturbed rates over grant Terms strictly before 2025
  (parsed rows 2017–2024: 360/516 = 69.8%).

## Corpus (`fedcourts query`)

- `uv run fedcourts query --court scotus --citation "599 U.S. 465" --limit 3`
  (known-case lookup for Jones v. Hendrix) — returned no rows.
  stderr: `ranged corpus reads: 1346 GET(s), 352452608 byte(s)`
  stderr note: citation coverage is sparse (159 of 590591 scotus rows carry
  citation data), so the empty result is a coverage gap, not absence.
  No further corpus queries — the sparse-filter guidance says not to retry.

## CourtListener MCP

Three `search` calls, all attempting to pull the Fifth Circuit opinion below
(Johnson v. Guerrero, No. 23-70002, July 23, 2025) — pre-decision material:

1. `type=o, court=ca5, q="Johnson v. Guerrero successive habeas 'previously
   unavailable'", filed 2025-07-01..2026-02-01` — 0 results.
2. `type=o, court=ca5, case_name="Johnson v. Guerrero"` — 0 results.
3. `type=o, court=ca5, docket_number="23-70002"` — 0 results.

The opinion is not in CourtListener's opinion index under those keys; I relied
on the petition's and BIO's quotation of it instead and stopped retrieval
there.

No web searches were used. No material about this case's own (nonexistent)
merits outcome was sought or surfaced.
