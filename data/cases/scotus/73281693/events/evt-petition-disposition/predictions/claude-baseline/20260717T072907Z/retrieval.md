# Retrieval log — scotus/73281693 evt-petition-disposition (claude-baseline, 20260717T072907Z)

Mode: `forward` (unrestricted retrieval; no outcome exists to leak).

## Corpus lookups (`fedcourts` CLI)

1. `uv run fedcourts query --court scotus --citation "600 U.S. 447" --limit 8`
   — 0 rows. stderr: `ranged corpus reads: 420 GET(s), 110100480 byte(s)`
2. `uv run fedcourts query --court scotus --era 2020s --citation "42 U.S.C. § 2000e" --limit 8`
   — 0 rows. stderr: `ranged corpus reads: 420 GET(s), 110100480 byte(s)`
3. `uv run fedcourts query --court scotus --era 2020s --limit 5`
   — 5 rows returned but with null captions/topics (sparse metadata), so not
   usable as substantive priors. stderr: `ranged corpus reads: 420 GET(s), 110100480 byte(s)`

Base rates: read the committed `metrics/statpack.md` (modern discretionary-cert
disposition, originating-circuit, relist, and CVSG cuts; per-Term paid/IFP
grant rates from `metrics/statpack.json`). No salience-band table is present
in the committed statpack build.

## CourtListener MCP lookups

1. `search(type=d, court=scotus, q="undue hardship" "religious accommodation", filed_after=2025-09-01)` — 0 results.
2. `search(type=d, court=scotus, q=Kluge OR Rodrique OR "Atlantic City" OR Muscatine, filed_after=2025-06-01)` — 0 results.
3. `search(type=d, court=scotus, case_name=Kluge)` — 0 results.
4. `search(type=d, court=scotus, case_name=Petersen v. Snohomish)` — 0 results.

(SCOTUS dockets do not appear in the RECAP docket search index, so these
returned nothing; used to check for competing petitions on the same question.)

## Web searches

1. `Supreme Court cert petition Title VII undue hardship "reasonable concern" circuit split Petersen Snohomish`
   — surfaced one news item ([The Center Square](https://www.thecentersquare.com/washington/article_3ee0cc1f-651b-4306-9f09-005e9a6d7d15.html))
   confirming the petition is pending; no disposition information.
2. `Supreme Court grants certiorari 2026 Groff undue hardship religious accommodation Title VII case granted`
   — surfaced only *Groff v. DeJoy* (2023) commentary and general material; no
   evidence the Court has already granted a competing vehicle on this
   question. Nothing outcome-revealing about this case surfaced.
