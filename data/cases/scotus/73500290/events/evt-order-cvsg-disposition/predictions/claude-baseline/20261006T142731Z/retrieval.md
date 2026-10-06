# Retrieval log

## Corpus tooling

- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
  stderr: `ranged corpus reads: 28 GET(s), 7208960 byte(s)`
  Returned eight recent granted SCOTUS matters with no topical relation to
  this petition (the surface has no text filter); not used in the forecast.

## CourtListener MCP server

Both calls failed with HTTP 429 (daily rate limit exceeded, retry in about an
hour). No REST fallback was attempted, per the prompt contract.

- `search` type=d, court=scotus, q="Mosaic Health Sanofi" -> 429
- `search` type=o, court=ca6, q="United Biologics" Amerigroup "Illinois Brick" -> 429

## Web search and fetch (engine tools, forward mode)

- WebSearch: `"Mosaic Health" Sanofi Supreme Court certiorari petition Illinois Brick 2026`
  Surfaced the SCOTUSblog case page for No. 25-1070 and the Second Circuit opinion.
- WebSearch: `"United Biologics" Amerigroup Sixth Circuit rehearing en banc denied Bush "Illinois Brick" 164 F.4th`
  Surfaced the Sixth Circuit opinions, the en banc denial (164 F.4th 529), and a Sixth Circuit appellate blog post.
- WebSearch: `"United Allergy Services" Amerigroup Supreme Court 25-1388 Solicitor General invited`
  Surfaced this docket's own filings and the October 5, 2026 order list. Nothing about this petition's disposition surfaced; it is pending.
- WebFetch: https://www.scotusblog.com/cases/astrazeneca-pharmaceuticals-lp-v-mosaic-health-inc/
  Companion petition No. 25-1070: filed Mar 5 2026, Chamber of Commerce and EPSA amici, response requested Apr 30, BIO Jul 22, distributed for Sept 28 conference, CVSG Oct 5 2026.
- WebFetch: https://www.supremecourt.gov/orders/courtorders/100526zor_2a34.pdf
  The fetch tool could not extract text from the PDF; no local PDF text tools on the runner. Not relied on.
- WebFetch: https://www.sixthcircuitappellateblog.com/case-updates/en-banc-sixth-circuit-passes-on-antitrust-indirect-seller-case/
  Summary of Judge Bush's statement and Judge Murphy's concurrence on the en banc denial.

## Provisioned inputs read

`record/context.json`, `record/snapshots/2026-10-06.json`,
`record/documents/documents.json`, `questions-presented.txt`, `petition.txt`
(truncated at 300 pages, ends inside the panel opinion appendix),
`brief-in-opposition.txt`; `metrics/statpack.md` for base rates. The petition
and BIO were summarized by two read-only subagents working from the same files.
