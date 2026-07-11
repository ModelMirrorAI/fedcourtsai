# Retrieval log — scotus/73274796 evt-petition-disposition (claude-baseline, 20260711T174451Z)

Mode: `forward` (record/context.json) — retrieval unrestricted; the outcome does
not yet exist. Roughly 9 retrieval calls total, inside the ~25-call budget.

## Corpus lookups (`fedcourts`, ranged backend)

1. `uv run fedcourts query --court scotus --citation "494 U.S. 872" --corpus-backend ranged --limit 8`
   — priors citing *Employment Division v. Smith*; returned no rows.
   Stderr: `ranged corpus reads: 379 GET(s), 99352576 byte(s)`
2. `uv run fedcourts query --court scotus --era 2020s --disposition granted --corpus-backend ranged --limit 10`
   — recent granted petitions for timing/context (confirmed other petitions
   distributed for the 6/25/2026 conference were granted on 6/29/2026, so this
   case's end-of-Term silence reads as a hold, not a backlog).
   Stderr: `ranged corpus reads: 111 GET(s), 29097984 byte(s)`

## Base rates

- `metrics/statpack.md` (committed statpack): "Modern discretionary-cert
  petitions by disposition" (9/190 resolved granted) and "SCOTUS petitions by
  Term" (Term 2025: denied 91.3%, granted 5.6%, dismissed 3.1%).

## Web retrieval (engine WebSearch/WebFetch)

3. WebFetch `https://www.supremecourt.gov/DocketPDF/25/25-113/409896/20260526191106693_Renteria%205.26.26%20post%20proofs.pdf`
   — attempt to read the SG's CVSG amicus brief directly; **HTTP 403**.
4. WebSearch: `Renteria v. New Mexico Superintendent of Insurance solicitor general brief cert 25-113 health care sharing ministry`
   — located DOJ/OSG brief page, Cert Pool docket, SCOTUSblog case page.
5. WebFetch `https://www.justice.gov/osg/brief/renteria-v-new-mexico-office-superintendent-insurance` — **HTTP 403**.
6. WebFetch `https://www.justice.gov/crt/media/1443486/dl` — **HTTP 403**.
7. WebFetch `https://certpool.com/dockets/25-113` — mirrored docket; confirms
   distributions and that no cert order has issued; no SG recommendation text.
8. WebFetch `https://ahcsm.org/ahcsm-welcomes-supreme-courts-interest-in-renteria/`
   and `https://www.scotusblog.com/cases/renteria-v-new-mexico-office-of-the-superintendent-of-insurance/`
   — case status; SCOTUSblog confirms CVSG 5/26/2026 and pending status.
9. WebSearch: `Renteria New Mexico "brief for the United States as amicus curiae" 25-113 certiorari should be granted health care sharing`
   — search summary reports the SG recommended **holding the petition pending
   St. Mary Catholic Parish v. Roy, No. 25-581** (overlapping QP1) and found
   further review of the preemption question unwarranted.
10. WebSearch: `"St. Mary Catholic Parish" v. Roy Supreme Court 25-581 certiorari granted free exercise`
    — confirms cert granted 4/20/2026 in No. 25-581 (Colorado universal
    preschool; *Smith* general-applicability QPs), argument expected fall 2026
    (SCOTUSblog, Oyez, Becket, Washington Examiner).
11. WebSearch: `solicitor general Renteria "hold" "St. Mary" health sharing ministry cert petition recommendation June 2026`
    — second corroboration of the hold-for-St.-Mary recommendation.

**Caveat:** the SG brief's recommendation was never read from the primary PDF
(403 on supremecourt.gov and justice.gov); it rests on two independent
search-result summaries plus corroborating docket behavior. See `flags.json`.

## CourtListener MCP

Not used — the provisioned snapshot, documents, corpus, and web retrieval
covered what was needed; no MCP tool call errored.
