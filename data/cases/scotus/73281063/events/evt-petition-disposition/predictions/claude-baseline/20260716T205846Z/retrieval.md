# Retrieval log — scotus/73281063 evt-petition-disposition (claude-baseline, 20260716T205846Z)

Mode: `forward` (`record/context.json`), so retrieval was unrestricted; this
case's own disposition was never sought and does not appear in any source
consulted (its own docket, per the provisioned snapshot fetched 2026-07-16,
shows no disposition).

## Committed base-rate context

- `metrics/statpack.md` (+ per-Term/fee-class detail in `metrics/statpack.json`)
  — modern discretionary-cert base rates, relist/CVSG/circuit cuts. The
  salience-band table referenced in the prompt is not present in this
  statpack version.

## Corpus lookups (`fedcourts query`, ranged backend)

All three returned zero rows (no matching priors surfaced):

1. `uv run fedcourts query --court scotus --topic "voter registration proof of citizenship NVRA election" --limit 8`
   — `ranged corpus reads: 3 GET(s), 786432 byte(s)`
2. `uv run fedcourts query --court scotus --topic "election law voting" --limit 8`
   — `ranged corpus reads: 3 GET(s), 786432 byte(s)`
3. `uv run fedcourts query --court scotus --topic "standing" --limit 6`
   — `ranged corpus reads: 3 GET(s), 786432 byte(s)`

## CourtListener MCP lookups

1. `search` (type=d, court=scotus, docket_number=25-1017) — 0 results.
2. `search` (type=r, court=scotus, q="Mi Familia Vota") — 0 results.
3. `call_endpoint` dockets (court=scotus, docket_number=25-1017) — companion
   RNC v. Mi Familia Vota docket (CL id 73281056): date_terminated null,
   date_cert_granted null, date_modified 2026-06-29.
4. `call_endpoint` docket-entries (docket=73281056) — 0 rows (CL carries no
   entries for this SCOTUS docket).

## Web retrieval

1. WebFetch `https://www.supremecourt.gov/rss/cases/JSON/25-1017.json` —
   HTTP 403, no content retrieved.
2. WebSearch: `Supreme Court certiorari "Mi Familia Vota" RNC 25-1017 granted
   conference June 2026` — surfaced SCOTUSblog case pages, Democracy Docket
   coverage, and filed briefs.
3. WebFetch Democracy Docket, "Supreme Court will hear Arizona case that could
   badly weaken key federal law protecting voter registration" (June 29,
   2026) — Court agreed Monday (6/29/2026) to hear the Republican defense of
   the Arizona laws.
4. WebFetch SCOTUSblog case page for 25-1017 — certiorari granted 6/29/2026 on
   both questions presented; docket shows 6/18 and 6/25 conference
   distributions before the grant. No status shown for 25-1019 or 25-1022.

Total: 3 corpus calls, 4 MCP calls, 4 web calls — within the ~25-call budget.
