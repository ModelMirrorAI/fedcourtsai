# Retrieval log

## Corpus lookups (`fedcourts query`)

- `uv run fedcourts query --court scotus --disposition gvr --era 2020s` → `ranged corpus reads: 43 GET(s), 11272192 byte(s)`. Returned a slate of OT2025 GVRs (mostly SG-side, dated 2026-06-29/30); used only as shape (GVRs cluster on the conferences right after the controlling decision), not as a numeric anchor.
- `uv run fedcourts query --court scotus --disposition granted --era 2020s` → `ranged corpus reads: 4 GET(s), 1048576 byte(s)`. Not informative for this cell.

## Base rates

- `metrics/statpack.md`: "Modern discretionary-cert petitions by disposition", "by originating circuit" (ca5), "by relist count" (bucket 0), "by CVSG status" (none), "Cert petitions by salience band", "SCOTUS cert petitions by Term", and "Segment base rate by salience band (sal-v4)" (`federal` column, prior Terms pooled).

## CourtListener MCP

- `search` (opinions, scotus, "Hemani 922(g)(3)", filed after 2026-01-01) → HTTP 429 rate limit.
- `search` (dockets, scotus, docketNumber 25-935 / 25-1001 / 25-1029 / 25-1219) → 429, then retried without 25-1219 → 0 results.
- `search` (opinions, scotus, "Hemani", filed after 2026-06-01) → 429.
- `call_endpoint` dockets (court scotus, docket_number 25-935) → 429, then retried → docket 73280976 "United States v. Kevin LaMarcus Mitchell", filed 2026-02-06, not marked terminated.
- `call_endpoint` docket-entries (docket 73280976) → 429, then retried → 0 entries.

## Web

- WebSearch: "United States v. Hemani Supreme Court decision June 2026 922(g)(3) holding".
- WebSearch: "Supreme Court grants certiorari 922(g)(1) felon in possession Second Amendment 2026 October Term".
- WebSearch: "\"United States v. Mitchell\" 25-935 certiorari denied 922(g)(1) Fifth Circuit Supreme Court June 2026".
- WebSearch: "Supreme Court 922(g)(1) petitions pending September 2026 long conference after Hemani felon in possession cert" (surfaced this petition's own supremecourt.gov PDF and a CRS sidebar describing it as pending; nothing about its disposition, which does not yet exist).
- WebSearch: "\"Cockerham\" 25-1029 Supreme Court certiorari denied June 8 2026 felon in possession child support".
- WebSearch: "scotusblog \"United States v. Mitchell\" 25-935 922(g)(1) petition denied".
- WebFetch: lisa-legalinfo.com, "Supreme Court Rebuffs DOJ on Felon-In-Possession Review" (May 4, 2026) — Doucet denial.
- WebFetch: congress.gov CRS LSB11170 (HTML: 403; PDF `LSB11170.1.pdf` fetched and text-extracted locally with pypdf — turned out to be the May 2024 version, not used).
- WebFetch: en.wikipedia.org/wiki/United_States_v._Hemani — holding and lineup.
- WebFetch: law.cornell.edu/supremecourt/text/24-1234 — Hemani passages on §922(g)(1) and dangerousness.
- WebFetch: justice.gov OSG page for United States v. Mitchell (metadata only) and `mitchell_petition.pdf` (text-extracted locally with pypdf) — relief sought.
- WebFetch: congress.gov CRS LSB11108 `.5.pdf` — status of §922(g)(1) petitions as of March 2026.
- WebFetch: scotusblog.com/cases/united-states-v-cockerham/ — Cockerham docket history.
- WebFetch: thereload.com "Supreme Court Turns Down DOJ Appeal in Non-Violent Felon Gun Case" — Cockerham denial coverage.
- WebFetch: supremecourt.gov docket 25-935 (Mitchell) — full proceedings list.
- WebFetch: supremecourt.gov docket 25-1001 (Doucet) — full proceedings list.

No query touched this case's own disposition (none exists; the petition is distributed for 9/28/2026), and nothing under `data/qp-topics/` was read.
