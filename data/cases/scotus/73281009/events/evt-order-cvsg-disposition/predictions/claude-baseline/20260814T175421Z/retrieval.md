# Retrieval log — claude-baseline, run 20260814T175421Z

Beyond the provisioned inputs (snapshot, event definition, context,
questions-presented/petition/BIO texts) and the committed
`metrics/statpack.md`:

## Corpus lookups (`fedcourts query`)

1. `uv run fedcourts query --court scotus --era modern --text "..." --limit 8`
   — failed (`--text` is not an option; the surface is structured filters
   only). No transfer line.
2. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 6`
   — stderr: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`. Returned six
   rows, five of them application dockets (extension grants) rather than cert
   petitions; not informative for this cell, not used as an anchor.

## CourtListener MCP lookups

3. `search` (dockets, court=scotus, q=`docketNumber:25-962`) — 0 results;
   companion-petition status not confirmed via CourtListener. The provisioned
   snapshot already records the Vide link and the RNC respondents' brief in
   support.

## Web searches (forward mode — related-case status only)

4. WebSearch: "Baxter v. Philadelphia Board of Elections Pennsylvania Supreme
   Court decision date requirement mail ballots 2026" — case granted review
   Jan 17, 2025; no final decision found.
5. WebSearch: "Pennsylvania Supreme Court ruling undated mail ballots 'free
   and equal' Baxter decided" — confirmed argument set for September 10
   (2025); no decision found as of today. Key sources:
   [Democracy Docket case page](https://www.democracydocket.com/cases/pennsylvania-philadelphia-undated-and-wrongly-dated-mail-in-ballots-challenge/),
   [ACLU-PA press release](https://www.aclupa.org/press-releases/pa-supreme-court-to-hear-arguments-in-aclu-pas-case-over-mail-ballot-date-errors/),
   [State Court Report tracker](https://statecourtreport.org/case-tracker/baxter-v-philadelphia-board-elections),
   [Votebeat](https://www.votebeat.org/pennsylvania/2025/01/17/baxter-philadelphia-undated-misdated-mail-ballot-case/).

Neither web search sought or surfaced this petition's own disposition (none
exists — the cell is forward mode, CVSG pending).
