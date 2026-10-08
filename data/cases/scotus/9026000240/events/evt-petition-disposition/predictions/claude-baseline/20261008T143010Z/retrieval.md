# Retrieval log

Mode: `forward` (unrestricted retrieval). Nothing retrieved disclosed this petition's disposition; it is pending.

## Corpus (`fedcourts query`)

- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 6` — `ranged corpus reads: 28 GET(s), 7274496 byte(s)`. Returned recent grants (Marschner, Rhoney, DHS v. D.V.D., Missionaries of Saint John the Baptist, two interim applications); none analogous, used for shape only.
- `uv run fedcourts query --court scotus --disposition denied --era 2020s --limit 4` — `ranged corpus reads: 0 GET(s), 0 byte(s)`. Returned capital-case applications and a pro se denial; not analogous.
- A first attempt with a `--text` flag was rejected (no such option); no corpus read.

## Base rates

- `metrics/statpack.md`: modern discretionary-cert disposition table, originating-circuit cut (ca4), relist-count cut, CVSG cut, salience-band cut, per-Term table, and the *Segment base rate by salience band (sal-v4)* table (baseline column, Terms 2017–2025 pooled).

## CourtListener MCP

- `search` (opinions, ca4/vaed, "Johnson v. Fleming" OR "Hall v. Fleming" Locke Davey tuition, filed after 2026-01-01) — 0 results.
- `search` (dockets, scotus/ca4, Fleming "State Council of Higher Education") — 2 results: ca4 No. 26-1437 Johnson v. Fleming (not terminated), ca4 No. 25-1574 Hall v. Fleming (terminated 2026-05-13).
- `call_endpoint` docket-entries for ca4 docket 73188902 (No. 26-1437), newest first, 15 entries — appeal fully briefed; motion to submit on the briefs deferred pending panel assignment (Sept 28, 2026); December 8–11, 2026 argument-session conflict notices; similar-case notices referencing the Supreme Court petitions.

## Web

- WebSearch: `"Hall v. Fleming" 26-193 Supreme Court docket Virginia tuition assistance grant Locke v. Davey` — Fourth Circuit opinion (No. 25-1574, May 13, 2026), the Hall petition, an amicus brief on 26-193.
- WebSearch: `supremecourt.gov docket 26-193 Hall v. Fleming "Response Requested" OR "DISTRIBUTED" OR "waiver"` — SCOTUSblog case page.
- WebSearch: `Johnson v. Fleming Hall v. Fleming Supreme Court Virginia tuition grant religious majors October 2026 response requested` — ADF case pages, district court coverage.
- WebFetch: `https://www.supremecourt.gov/docket/docketfiles/html/public/26-193.html` — Hall petition filed Aug 11, 2026; response extended to Oct 14, 2026; thirteen amicus briefs; no distribution yet.
- WebFetch: `https://www.scotusblog.com/cases/hall-v-fleming/` — question presented (whether to overrule Locke v. Davey); pending.
