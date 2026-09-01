# Retrieval log

Beyond the provisioned snapshot, event definition, frozen context, and
the committed `metrics/statpack.md` (interim-docket section), this
forward-mode cell consulted:

## Corpus lookups

- `uv run fedcourts query --court scotus --include-applications
  --include-open --era 2020s --limit 10` — recent SCOTUS application
  priors; surfaced 26A203 (NPS v. National Trust — substantive,
  response requested, referred, granted) as the closest recent
  comparator.
  - `ranged corpus reads: 4 GET(s), 1048576 byte(s)`
- One earlier `fedcourts query` invocation was rejected for passing a
  free-text argument (usage error, no corpus read performed).

## Web searches

- WebSearch: "NRCC v. Brown Supreme Court emergency stay application
  26A274 FCC Fourth Circuit" — identified the dispute (lowest unit
  charge for party committees; CA4 vacatur of the FCC Media Bureau
  notice; CA4 stay denial with immediate effectiveness).
- WebSearch: "Supreme Court 26A274 stay lowest unit rate NRCC response
  September 2026" — CA4 2-1 stay denial detail (judgment entered
  Aug 25, 2026, effective immediately), applicants' pre-Sept. 4 timing
  goal, and the government response's arguments (standing, Hobbs Act
  jurisdiction, §315(b) merits).

## Web fetches

- SCOTUSblog, "Republican groups file emergency application to court on
  broadcasting rates for political ads" (Aug 2026) — fetched
  successfully; June 19 divided CA4 panel (King majority, Wilkinson
  dissent), March 30, 2026 Media Bureau notice, parties, arguments,
  Sept 3 noon response deadline, Trump administration brief backing
  applicants.
- supremecourt.gov PDF of the government's response (26A274) — HTTP 403,
  not retrieved.
- insideradio.com CA4 stay-denial article — HTTP 429, not retrieved
  (its content reached me via the search-result summaries above).

No CourtListener MCP lookups were made. No retrieval sought this
application's own disposition; it remains pending (response due
Sept 3, 2026, after this run).
