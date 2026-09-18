# Retrieval log

Beyond the provisioned inputs (snapshot `2026-09-17.json`, `context.json`, `documents/`), the event definition, `schemas/prediction.schema.json`, and the committed `metrics/statpack.md`:

## Corpus

- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
  stderr: `ranged corpus reads: 28 GET(s), 7340032 byte(s)`
  (Returned recent granted SCOTUS rows, mostly substantive applications and OT2025 cert grants; no comparable CVSG'd ERISA petition. Not relied on.)

## Web (forward mode; all predate the snapshot except where noted)

- WebSearch: `Aldridge v. Regions Bank 25-590 Solicitor General brief surcharge ERISA recommend` — surfaced the SCOTUSblog case page, the Sixth Circuit opinion listings, Samuel Bray's blog post, and the petition PDF. No disposition surfaced.
- WebFetch: `https://www.supremecourt.gov/docket/docketfiles/html/public/25-590.html` — docket entries (identical to the snapshot's 16 entries; nothing later than the 9/16/2026 supplemental brief) and document links.
- WebFetch: `https://www.supremecourt.gov/DocketPDF/25/25-590/422539/20260831142837907_25-590_Aldridge_Final.pdf` — Brief for the United States as amicus curiae (Aug 31, 2026). Fetcher could not read the PDF text; text extracted locally with pypdf from the saved file. Recommendation: deny (vehicle grounds; agrees CA6 erred and a split exists).
- WebFetch: `https://www.supremecourt.gov/DocketPDF/25/25-590/424443/20260916105340066_Aldridge%20Supplemental%20Reply_Final.pdf` — Petitioners' supplemental brief (Sep 16, 2026); same local extraction.
- WebFetch: `https://www.scotusblog.com/cases/aldridge-v-regions-bank/` — case page; proceedings list; no disposition; no summary of the SG brief.
- WebFetch: `https://blog.dividedargument.com/p/equity-erisa-and-the-surcharge-remedy` — Samuel Bray, Jan 29, 2026, on his amicus brief in support of the petition.

## CourtListener MCP

- None used.

No search surfaced this petition's disposition; the case is pending for the October 9, 2026 conference.
