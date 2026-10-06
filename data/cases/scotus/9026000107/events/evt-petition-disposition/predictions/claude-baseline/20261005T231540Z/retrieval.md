# Retrieval log

Mode: `forward` (pending petition). Retrieval unrestricted; no outcome for this case exists, and none surfaced.

## Corpus tooling

- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 12`
  stderr: `ranged corpus reads: 28 GET(s), 7208960 byte(s)`
  Purpose: shape of recent grants (distribution counts, originating courts). Returned mostly 2026 stay applications and three cert grants; not used for a number.
- Base rates: the committed `metrics/statpack.md` (modern discretionary-cert disposition section; relist-count, CVSG and salience-band cuts; the per-Term "Segment base rate by salience band (sal-v4)" table, pooled over OT2017–OT2025 for `baseline` bracketed `reached`).

## CourtListener MCP

- `search` (type `d`, court `scotus`, q `Tedford's Tenancy`): 0 results. The companion petition is not yet in CourtListener's SCOTUS docket index.

## Web searches

- `"Walls v. Prince George's County" certiorari Supreme Court 26-107 ripeness takings` — surfaced the Pacific Legal Foundation case page and press release (July 2026), the NAR consolidated amicus brief (Nos. 26-107 and 26-110), and the petition appendix on supremecourt.gov.
- `"Tedford's Tenancy" Supreme Court petition certiorari 2026 ripeness takings New York` — surfaced the companion petition (filed June 30, 2026), PLF's case page, an inversecondemnation.com post (July 2026), NAR's August 27, 2026 announcement, and a Marzulla Law post.

## Web fetches

- `https://www.supremecourt.gov/docket/docketfiles/html/public/26-110.html` — companion docket: distributed for 9/28/2026 conference on Sep 2; response requested Sep 9 (due Oct 9); respondent's extension motion Oct 1, granted in part Oct 2, response now due November 10, 2026. Same amicus slate as this case. Forward signal predating nothing I am forecasting; used for the timing and companion reasoning.
- `https://www.supremecourt.gov/docket/docketfiles/html/public/26-107.html` — this case's public docket as of fetch: no entry after the October 1 BIO; matches the provisioned snapshot. No disposition surfaced.
- `https://marzulla.com/blog/is-ripeness-in-the-context-of-taking-claims-ripe-for-supreme-court-review/` — August 28, 2026 practitioner post discussing both petitions; advocacy for a grant, no prediction.

Total: 1 corpus query, 1 MCP call, 2 web searches, 3 fetches.
