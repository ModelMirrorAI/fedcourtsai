# Retrieval log

Beyond the provisioned inputs (snapshot 2026-08-16, `record/documents/`
petition / questions-presented / brief-in-opposition — the last carrying both
the BIO and respondent's merits brief — and `record/context.json`) and the
committed `metrics/statpack.md`:

## Corpus lookups

1. `uv run fedcourts query --court scotus --citation "603 U.S. 109" --limit 5`
   — attempted known-case lookup for *SEC v. Jarkesy*; returned no rows.
   stderr: `ranged corpus reads: 1329 GET(s), 348389376 byte(s)` and a `note:`
   line stating the citation column covers 161 of 590,339 scotus-scope rows
   (coverage gap, not absence of the precedent). No further corpus queries —
   the sparse-filter guidance says not to retry.

## Web searches (forward cell; retrieval unrestricted)

2. Web search: `FCC v. AT&T Supreme Court 2026 decision Seventh Amendment
   forfeiture holding` — to learn the holding of an intervening OT2025
   decision cited throughout respondent's merits brief (postdates my training
   data). Sources used: the Congress.gov CRS sidebar (LSB11440), the FCC press
   page, and the slip-opinion listing (25-406, 2026-06-04): 8–1, Roberts,
   C.J.; FCC forfeiture orders do not violate the Seventh Amendment because
   they are not self-enforcing — collection requires a de novo jury trial —
   distinguishing *Jarkesy*; Thomas dissenting.
3. Web search: `Sripetch v. SEC Supreme Court 2026 decision disgorgement
   Jarkesy holding` — same purpose (25-466, 2026-06-04): unanimous; SEC
   disgorgement does not require proof of investor pecuniary loss; Thomas
   concurring on a reserved Seventh Amendment question. Marginal to this
   forecast.
4. Web search: `"Sun Valley Orchards" Supreme Court 25-966 cert granted merits
   briefing analysis Jarkesy H-2A` — pre-decision commentary and docket
   context only (SCOTUSblog case page, Fisher Phillips and CAC case pages,
   Oyez). The case is undecided (argument set 2026-11-10); nothing
   outcome-revealing exists, and none was sought.

No CourtListener MCP lookups were made (the provisioned documents and the web
results above covered what was needed within budget).
