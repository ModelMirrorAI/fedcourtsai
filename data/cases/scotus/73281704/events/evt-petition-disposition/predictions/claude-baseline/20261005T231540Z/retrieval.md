# Retrieval log

Beyond the provisioned inputs (snapshot, context.json, QP, petition, BIO) and `metrics/statpack.md`:

## Corpus (fedcourts CLI)

1. `uv run fedcourts paths --court scotus --docket 73281704 --event evt-petition-disposition --role predictor` (path resolution only).
2. `uv run fedcourts query --court scotus --limit 12 --disposition granted` — stderr: `ranged corpus reads: 28 GET(s), 7208960 byte(s)`. Used only to see the shape of recent grants (long-conference grants dated 9/29 and 10/1/2026); no prior resembled this case.
3. `uv run fedcourts query --court scotus --limit 8` — stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`. Recent resolved rows; not informative for this case.

## CourtListener MCP

4. `search` type=d, court=scotus, docket_number=25-7026 — 0 results.
5. `call_endpoint` dockets, court=scotus, docket_number=25-7026 — found docket id 73283862, *Corey Duran Berry v. United States*, filed 2026-03-12, not terminated.
6. `search` type=d, court=scotus, q="Berry v. United States", filed_after 2026-02-01 — 0 results.
7. `call_endpoint` docket-entries, docket=73283862 — 0 entries (CourtListener carries no entries for this SCOTUS docket).

## Web (supremecourt.gov, public docket and filings of the companion case)

8. Fetched `https://www.supremecourt.gov/docket/docketfiles/html/public/25-7026.html` (Berry docket: CFR 4/8/2026; amici 5/8; BIO 5/27; distributions 6/18, 6/25, 9/28, 10/9/2026; supplemental brief 8/5/2026). Fetched a second time for the PDF links and counsel.
9. Fetched `https://www.supremecourt.gov/docket/docketfiles/html/public/24-571.html` (*Young v. United States*: response requested 12/23/2024, denied 4/28/2025).
10. Fetched the Berry BIO, petition, and 8/5/2026 supplemental brief PDFs from the 25-7026 docket and extracted their text locally with pypdf (the fetch tool's summarizer could not read the PDFs). Read: the supplemental brief in full; the BIO's argument section; the petition's question presented and front matter.

No search touched this case's own disposition; its docket page was not fetched (the snapshot is dated today). Nothing under `data/qp-topics/` was read.
