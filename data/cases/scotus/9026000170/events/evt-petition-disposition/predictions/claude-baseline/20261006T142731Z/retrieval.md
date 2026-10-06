# Retrieval log

## Corpus tooling

- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
  stderr: `ranged corpus reads: 28 GET(s), 7208960 byte(s)`
  Result: eight recent granted rows (immigration, stay applications, a family-law case); no patent or § 314(d) neighbor. Not used for the number.
- `metrics/statpack.md` (committed): sal-v4 segment base-rate table (pooled baseline `reached` OT2017–OT2025), relist-count cut, CVSG cut, originating-circuit cut (cafc).

## CourtListener MCP

- `search` (type d, court scotus, "Dolby Laboratories Licensing Unified Patents") — HTTP 429, daily rate limit exceeded (1400/day), reset in ~53 minutes.
- `search` (type o, court cafc, Federal Express Qualcomm "real parties in interest" 314(d)) — HTTP 429, same limit.
- No further MCP calls attempted; proceeded on provisioned inputs plus the sources below.

## Web

- WebSearch: "Dolby Laboratories v. Unified Patents 25-1011 Supreme Court certiorari real party in interest 314(d) response requested" — located the 25-1011 docket page, the SG's opposition brief listing, and an IPWatchdog item reporting the June 22, 2026 denial.
- WebFetch: https://www.supremecourt.gov/docket/docketfiles/html/public/25-1011.html — full proceedings list for Dolby (petition Feb 20, 2026; two SG extensions; Director's BIO May 21; Unified's BIO May 26; distributed June 2 for the June 18 conference; denied June 22, 2026). Pre-dates this cell's snapshot.
- WebFetch: https://www.justice.gov/osg/brief/dolby-laboratories-licensing-corp-v-unified-patents-llc — confirmed the SG's filing in Dolby was a petition-stage brief in opposition (brief text not on the page).

## Repository

- `data/cases/scotus/73281051/events/evt-petition-disposition/event.yaml` and `data/cases/scotus/72465990/.../event.yaml` — found by a grep for "Dolby" / "ESIP" to confirm the companion cases exist in the corpus; neither has a provisioned snapshot in git and I did not open either case's `outcome.json`.
- Nothing under `data/qp-topics/` was read.
