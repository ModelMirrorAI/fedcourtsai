# Retrieval log

## Corpus tooling

- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
  stderr: `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
  Returned five generic recent granted rows (interim applications and one
  paid petition); no subject filter reaches RLUIPA, so used only to confirm
  the tooling worked. Not weighted in the forecast.
- `metrics/statpack.md` (committed): modern discretionary-cert base rates;
  relist-count, CVSG, and salience-band cuts; *Segment base rate by salience
  band (sal-v4)* table, pooled `elevated` `reached` over Terms 2017 to 2024
  = 17.2% (n=2810). This is the anchor.

## CourtListener MCP

1. `search` type=d court=scotus docket_number=25-965 — 0 results (SCOTUS
   dockets not indexed by that number).
2. `search` type=o court=ca3 q="Anash Borough of Kingston RLUIPA" — 1 result:
   Anash Inc v. Borough of Kingston, No. 25-1097, filed 2026-07-30, Published,
   cluster 10936715. Confirms the post-petition Third Circuit decision the
   BIO addresses.
3. `search` type=d court=scotus q="Spirit of Aloha Temple" — 0 results.
4. `search` type=d court=scotus q=Grand "University Heights" — 0 results.
5. `search` type=o court=ca6 q=Grand "University Heights" prayer — 1 result:
   Daniel Grand v. City of University Heights, Ohio, No. 24-3876, filed
   2025-11-13, Published, cluster 10735939.
6. `get_endpoint_item` clusters/10735939 — panel Sutton, Batchelder, Larsen;
   no syllabus text.

## Repository data read for related-case context (not this case's outcome)

- `data/cases/scotus/73281006/events/evt-order-judgment/event.yaml` — Grand
  v. City of University Heights merits event, opened at grant 2026-06-30.
- `data/cases/scotus/73281006/events/evt-order-judgment/predictions/claude-baseline/20260816T111104Z/predicted_reasoning.md`
  — my own predictor's earlier merits forecast for Grand, read only to learn
  Grand's question presented (ripeness under Williamson County finality).

No web searches. Nothing under `data/qp-topics/` was read. No material about
this petition's disposition was sought or surfaced.
