# Retrieval log

## Corpus (`fedcourts query`, via the cell's corpus service)

1. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 8`
   stderr: `ranged corpus reads: 28 GET(s), 7340032 byte(s)`
   Returned eight 2020s grant-family rows, mostly substantive interim
   applications and unrelated cert grants; no expropriation or act-of-state
   analogue surfaced. Used only as a sanity check on the corpus's shape.
2. `uv run fedcourts query --court scotus --citation "581 U.S. 170" --citation "604 U.S. 115" --citation "592 U.S. 169"`
   stderr: `ranged corpus reads: 9 GET(s), 2293760 byte(s)`
   Empty; the tool printed its `note:` line that only about 200 scotus rows
   carry any reporter citation. Coverage gap, not absence of the cases.

## CourtListener MCP

3. `search` type=d court=scotus docket_number=25-1256 — 0 results (search index
   does not carry this docket).
4. `call_endpoint` dockets, court=scotus docket_number=25-1256 — returned docket
   id 73302615, date_filed 2026-05-06, date_terminated null. Confirms the
   petition is pending (forward cell correctly provisioned). No docket entries
   fetched.
5. `search` type=o court=cadc q="Helmerich" "Petróleos de Venezuela" Hickenlooper,
   filed_after 2025-09-01 — one hit: the D.C. Circuit opinion of 2025-10-03,
   No. 24-7161 (cluster 10690213). Existence and date confirmed only; the
   opinion body was not read (the petition appendix summary and the BIO's
   account were sufficient).

## Committed base rates

- `metrics/statpack.md`: Modern discretionary-cert petitions by disposition;
  by originating circuit (cadc row); relist-count and CVSG cuts (paid scored
  segment); Cert petitions by salience band; Segment base rate by salience
  band (sal-v4), pooled over Terms 2017–2024.

No web searches.
