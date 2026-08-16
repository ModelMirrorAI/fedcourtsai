# Retrieval log

Beyond the provisioned inputs (snapshot, `event.yaml`, `record/context.json`,
`record/documents/` texts) and the committed `metrics/statpack.md`:

## Corpus lookups (`fedcourts`)

1. `uv run fedcourts query --court scotus --citation "574 U.S. 418" --limit 3`
   (known-case lookup for Hana Financial as a prior) — returned no rows.
   stderr transfer line: `ranged corpus reads: 1329 GET(s), 348389376 byte(s)`
   stderr note line: `note: citations filter: 161 of 590339 rows in scope (scotus)
   carry citation data, and the column holds a case's OWN reporter cites (not a
   cases-citing-this-authority graph) — an empty result here usually means missing
   data, not no match`
   (An earlier invocation with a `--text` flag was rejected as usage error — no
   such option — and read nothing.)

## Web retrieval (forward cell — unrestricted)

2. WebFetch `https://www.supremecourt.gov/DocketPDF/24/24-1016/409398/20260520181120660_RiseandShine_CVSG%20v2.pdf`
   (the SG's CVSG amicus brief) — **HTTP 403 Forbidden**, no content retrieved.
3. WebSearch: `RiseandShine Rise Brewing PepsiCo solicitor general brief 24-1016
   CVSG recommendation trademark strength` — surfaced SCOTUSblog case page,
   justice.gov OSG brief page, Patently-O commentary, Mondaq commentary, and the
   supremecourt.gov docket/brief PDFs.
4. WebFetch `https://www.justice.gov/osg/brief/riseandshine-corp-v-pepsico` —
   **HTTP 403 Forbidden**, no content retrieved.
5. WebFetch `https://patentlyo.com/patent/2026/07/rise-and-grind-the-court-takes-up-whether-trademark-strength-is-fact-or-law.html`
   — retrieved. Supplied the SG's bottom line (Second Circuit "mischaracterized
   the inquiry," but deny on vehicle grounds) and the cert-grant framing used in
   `reasoning.md`. This is the secondhand source for the SG's position.

## CourtListener MCP

None — the docket record and provisioned documents covered the case history, and
the merits briefs do not exist yet at this moment.

No retrieval sought this case's outcome: the judgment does not exist (forward
cell; merits briefing due August 31 / October 19, 2026).
