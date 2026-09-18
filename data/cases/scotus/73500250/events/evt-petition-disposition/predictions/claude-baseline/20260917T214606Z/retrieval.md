# Retrieval log

## Corpus (`fedcourts query`)

- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
  stderr: `ranged corpus reads: 28 GET(s), 7340032 byte(s)`
  Returned recent granted rows (mostly OT2026 emergency applications and a few OT2025 paid petitions with multiple relists); used only as shape context, not as a matched prior set.

## CourtListener MCP

1. `search` (type=o, court=ca5, filed_after=2026-01-01, q: Delgado 242 1519 Customs and Border Protection) — located *United States v. Delgado*, No. 24-50784, cluster 10803268, opinion 11269998, filed 2026-03-03, Published.
2. `read_document` (opinion_id=11269998, chunks 0–3 of 5) — read the Fifth Circuit opinion's facts, standard of review, and § 242 analysis (willfulness grounds; excessive-force and injury findings for both incidents).
3. `search` (type=d, court=scotus, docket_number=25-1347) — no results in the search index.
4. `call_endpoint` dockets (id=73500250) — docket exists, `date_terminated: null`, no disposition surfaced.
5. `call_endpoint` docket-entries (docket=73500250) — zero entries mirrored; the provisioned snapshot is the only docket text used.

## Committed base rates

- `metrics/statpack.md`: "Modern discretionary-cert petitions by disposition", "by originating circuit" (ca5 row), "by relist count", "by CVSG status", "by salience band", and "Segment base rate by salience band (sal-v4)" (baseline column, Terms 2017–2024 pooled).

No web searches.
