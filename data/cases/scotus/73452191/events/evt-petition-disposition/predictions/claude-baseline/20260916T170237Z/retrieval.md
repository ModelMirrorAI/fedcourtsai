# Retrieval log

Forward cell; retrieval unrestricted. Nothing consulted touches this docket's own disposition (the conference is September 28, 2026, after this run).

## Corpus

- `uv run fedcourts query --court scotus --era 2020s --disposition granted`
  stderr: `ranged corpus reads: 47 GET(s), 12320768 byte(s)`
  Result: recency-ranked granted rows, mostly substantive emergency applications (People Not Politicians v. Onder, NRCC v. Brown, National Park Service v. National Trust, Trump v. California) and unrelated OT2025 cert grants (Jouppi v. Alaska, Viramontes v. Cook County, Grant v. Higgins, Grand v. University Heights). No judicial-immunity prior surfaced; used only to confirm the query surface has no topic filter for SCOTUS rows.

## CourtListener MCP

1. `search type=o court=ca3 q="Bernard Ignelzi"` — 0 results (the decision below is unpublished and not indexed).
2. `search type=d court=scotus q="Goldston Gibson"` — 0 results.
3. `search type=d court=scotus q="Eighmy Rockett"` — timed out.
4. `search type=o q="Ignelzi judicial immunity" filed_after=2024-01-01` — 0 results.
5. `search type=o court=[scotus,ca4] q="Goldston judicial immunity search home"` — Matthew Gibson v. Louise Goldston, CA4 No. 22-1757, published, filed 2023-10-30 (confirms the Fourth Circuit case the petition relies on).
6. `search type=o court=[scotus,ca8] q="Eighmy judicial immunity jail"` — D. Bart Rockett v. Eric Eighmy, 71 F.4th 665, CA8 No. 21-3903, published, filed 2023-06-22 (confirms the Eighth Circuit case).

## Statpack

- `metrics/statpack.md`: modern discretionary-cert disposition section; relist-count and CVSG cuts (paid scored segment); originating-circuit table; "Segment base rate by salience band (sal-v4)" per-Term table, pooled over OT2017 to OT2024.

No web searches.
