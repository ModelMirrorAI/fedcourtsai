# Retrieval log

Beyond the provisioned inputs (`record/snapshots/2026-10-08.json`, `record/context.json`, `record/documents/{questions-presented,petition,brief-in-opposition}.txt`, `documents.json`, `event.yaml`) and the committed `metrics/statpack.md`:

## Corpus tooling

- `uv run fedcourts paths --court scotus --docket 73500293 --event evt-petition-disposition --role predictor`
- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
  - stderr: `ranged corpus reads: 28 GET(s), 7274496 byte(s)`
  - Returned five recent granted/decided SCOTUS rows unrelated to copyright (no subject filter is available on SCOTUS rows); not used in the forecast.
- An initial `fedcourts query ... --text "..."` attempt was refused (no such option) and ran no query.

## CourtListener MCP

- `search` (type `o`, court `ca5`, q: `Vetter Resnik termination "Double Shot"`): one result, *Vetter v. Resnik*, No. 25-30108, filed 2026-01-12, status Published, cluster 10773393. Used only to confirm publication status.

## Web (forward mode, pre-decision material only)

- Fetched `https://www.supremecourt.gov/docket/docketfiles/html/public/25-1391.html` to locate the reply brief URL and confirm no docket entry postdates September 30, 2026 (none does).
- Fetched the reply brief PDF `https://www.supremecourt.gov/DocketPDF/25/25-1391/426032/20260930115123431_2026-09-30%20Final%20Vetter%20Reply.pdf` and extracted its text locally with pypdf. Read in full; used for the vehicle answer and the CVSG invitation.

No search was made for this case's disposition, and none was encountered. Nothing under `data/qp-topics/` was read.
