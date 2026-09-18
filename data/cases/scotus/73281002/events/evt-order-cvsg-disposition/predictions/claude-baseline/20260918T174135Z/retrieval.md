# Retrieval log

## Corpus tooling

- `uv run fedcourts query --court scotus --era 2020s --disposition granted`
  — stderr: `ranged corpus reads: 47 GET(s), 12320768 byte(s)`. Returned
  recent granted SCOTUS priors (OT2025 grants, including several 2026-06-29
  grants). Used only for the population's shape; no close Anderson-Burdick
  analogue among them, so no adjustment was taken from these rows.

## CourtListener MCP

- `get_endpoint_item dockets 73281002` — docket shell for No. 25-962 (RNC v.
  Bette Eakin, filed 2026-02-13, `date_terminated: null`). No disposition
  disclosed.
- `call_endpoint docket-entries docket=73281002` — 0 entries returned;
  CourtListener carries no entries for this docket, so the live-docket check
  could not confirm whether the SG has filed.
- `search type=d court=scotus docket_number=25-967` — 0 results (companion
  Commonwealth of Pennsylvania petition not found).
- `search type=d court=scotus case_name=Eakin filed_after=2026-01-01` — 0
  results.
- `search type=o court=pa q='Baxter "Philadelphia Board of Elections" date'
  filed_after=2025-06-01` — 0 results.
- `search type=o court=pa q='Baxter mail ballot "Free and Equal Elections"'
  filed_after=2025-09-01` — 0 results. Status of the Pennsylvania Supreme
  Court's *Baxter* decision therefore unconfirmed.

## Committed base rates

- `metrics/statpack.md`: CVSG cut (paid scored segment), relist-count cut,
  and the sal-v4 per-Term salience band table (band `high`, bracketed
  `reached`, pooled over Terms 2017–2024).

No web searches.
