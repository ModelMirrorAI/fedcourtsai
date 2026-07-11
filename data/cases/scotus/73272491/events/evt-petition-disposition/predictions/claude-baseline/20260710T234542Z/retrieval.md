# Retrieval log — scotus/73272491 / evt-petition-disposition / claude-baseline / 20260710T234542Z

## Corpus lookups (`fedcourts`, ranged backend)

1. `uv run fedcourts query --court scotus --citation "530 U.S. 466" --citation "567 U.S. 343" --citation "516 U.S. 29" --limit 8`
   - stderr: `ranged corpus reads: 378 GET(s), 99090432 byte(s)`
   - Result: no matching priors returned.
2. `uv run fedcourts query --court scotus --citation "516 U.S. 29" --limit 5`
   - stderr: `ranged corpus reads: 378 GET(s), 99090432 byte(s)`
   - Result: no matching priors returned.

Base rates: read the committed `metrics/statpack.md` (SCOTUS resolved base
rate — granted 1.4%, denied 4.4%, other 78.4%, over 296 resolved cases). The
statpack as committed has no "Modern discretionary-cert petitions by
disposition" section (see `flags.json`).

## CourtListener MCP

The configured CourtListener MCP server failed on every call with a
server-side error (`REDIS_URL is not set; cannot access session store`):

1. `search` (opinions, scotus, q="Ellingburg restitution") — error, no data.
2. `search` (opinions, scotus, q="Ellingburg") — retry, same error.

No CourtListener data informed this prediction.

## Web searches (engine fallback, forward mode)

1. `Ellingburg v. United States Supreme Court decision restitution criminal punishment holding`
   — used to verify the holding and date of Ellingburg v. United States,
   No. 24-482 (Jan. 20, 2026): MVRA restitution is criminal punishment for Ex
   Post Facto purposes, 9-0 (Kavanaugh, J.), Thomas concurrence joined by
   Gorsuch. Sources: supremecourt.gov slip opinion (24-482_d1oe.pdf),
   congress.gov CRS LSB11397.
2. `Mizrahi v. United States 25-1238 certiorari Libretti forfeiture Supreme Court`
   — surfaced the Washington Legal Foundation case page for its June 1, 2026
   cert-stage amicus brief (wlf.org/case/mizrahi-v-united-states/); confirmed
   the amicus coalition already visible on the docket snapshot. No
   outcome-revealing material exists (the petition is pending).
