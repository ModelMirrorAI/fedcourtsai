# Retrieval log

Beyond the provisioned inputs (snapshot 2026-08-16, `petition.txt`,
`brief-in-opposition.txt`, `questions-presented.txt`, `documents.json`,
`event.yaml`, `record/context.json`) and the committed `metrics/statpack.md`
(merits-docket section, cert cuts read for orientation only):

## Corpus tooling

- `uv run fedcourts query --court scotus --citation "441 U.S. 677" --citation "544 U.S. 167" --limit 5`
  - stderr: `ranged corpus reads: 1329 GET(s), 348389376 byte(s)`
  - Returned zero rows, with the coverage note: `citations filter: 161 of
    590339 rows in scope (scotus) carry citation data, and the column holds a
    case's OWN reporter cites (not a cases-citing-this-authority graph)`.
    Per the sparse-filter guidance I did not retry.

## Web retrieval (forward mode — unrestricted)

- WebSearch: `Crowther v. Board of Regents Supreme Court cert granted Title IX
  employees private right of action` — case coverage, circuit-split detail,
  OT2026 argument expectation.
- WebSearch: `Crowther Board of Regents solicitor general CVSG brief
  recommendation Title IX "views of the United States"` — located the CVSG
  brief mirrors and coverage.
- WebFetch (used):
  - https://www.scotusblog.com/cases/crowther-v-board-of-regents-of-the-university-system-of-georgia/
    — case page (QP, dates; no SG position detail).
  - https://www.scotusblog.com/2026/05/court-agrees-to-hear-case-on-ability-of-employees-to-bring-certain-suits-for-sex-discrimination-/
    — grant coverage; source for the SG recommending grant while supporting
    the university's position.
  - https://www.littler.com/news-analysis/asap/us-supreme-court-decide-whether-educational-employees-can-sue-under-title-ix
    — corroboration of the SG's merits skepticism; 8–3 split detail
    (1st/2d/3d/4th/6th/8th/9th/10th vs 5th/7th/11th).
- WebFetch (failed, HTTP 403 — no content retrieved):
  - https://www.supremecourt.gov/DocketPDF/25/25-183/404072/20260409172353690_25-183_Crowther_CVSG.pdf
  - https://www.scotusblog.com/wp-content/uploads/2026/04/25-183_crowther_cvsg.pdf
  - https://www.justice.gov/osg/brief/crowther-v-board-regents-univ-sys-ga
  - https://www.ropesgray.com/en/insights/alerts/2026/06/supreme-court-to-resolve-circuit-split-on-title-ix-employment-discrimination-claims
  - https://www.relistwatch.com/case/25-183

No CourtListener MCP calls were made: the docket, filings, and QP were already
provisioned, and the open-web fetches covered the CVSG-position question.
