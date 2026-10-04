# Retrieval log

## Corpus (`fedcourts query`, via the cell's corpus service)

1. `uv run fedcourts query --court scotus --citation "598 U.S. 175" --citation "561 U.S. 477" --citation "603 U.S. 109"`
   stderr: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   Result: empty, with a `note:` that only about 200 SCOTUS rows carry any reporter citation (coverage gap, not absence).
2. `uv run fedcourts query --court scotus --disposition granted --era 2020s`
   stderr: `ranged corpus reads: 39 GET(s), 10223616 byte(s)`
   Result: about 20 recent granted rows (mostly OT2025 applications and petitions), none topically related to jurisdiction-stripping or structural claims; used only to confirm the surface works, not as priors.

## CourtListener MCP

All three calls failed with `HTTP 429: Request was throttled. Rate limit exceeded: 300/hour. Expected available in 1139 seconds.` No results were obtained and no further MCP calls were attempted.

1. `search(type=o, court=ca5, q='Moats "National Credit Union Administration"')` — the Fifth Circuit opinion in this case.
2. `search(type=d, court=scotus, docket_number=25-735, q='"United States Congress" Johnson')` — status of the lead case the petition asks to be held for.
3. `search(type=o, filed_after=2023-04-01, q='"1818(i)" Axon "structural" constitutional preclusion "no court shall have jurisdiction"')` — post-Axon circuit decisions on express preclusion.

## Statpack

`metrics/statpack.md`: *Modern discretionary-cert petitions by disposition*, *by originating circuit*, *by relist count (paid scored segment)*, *by CVSG status (paid scored segment)*, *by salience band*, *SCOTUS cert petitions by Term*, and *Segment base rate by salience band (sal-v4)*.

## Web searches

None.
