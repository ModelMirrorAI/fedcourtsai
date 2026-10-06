# Retrieval log

Provisioned inputs read: `record/context.json`, `record/snapshots/2026-10-06.json`, `record/documents/documents.json`, `questions-presented.txt`, `petition.txt`, `brief-in-opposition.txt`, plus `event.yaml`, `AGENTS.md`, `.github/prompts/predict.md`, `schemas/prediction.schema.json`, and the committed `metrics/statpack.md` (modern cert by disposition, originating circuit, relist, CVSG, salience band, per-Term, and the sal-v4 segment base rate table).

## Corpus lookups

- `uv run fedcourts paths --court scotus --docket 73500290 --event evt-petition-disposition --role predictor`
- `uv run fedcourts query --court scotus --era 2020s --disposition granted` — `ranged corpus reads: 48 GET(s), 12451840 byte(s)`
- `uv run fedcourts query --court scotus --era 2020s --disposition denied` — `ranged corpus reads: 0 GET(s), 0 byte(s)`

Both queries returned recency-ranked modern SCOTUS rows (most recently resolved first); neither surfaced a CVSG-conditioned or antitrust-specific prior, and they did not move the forecast.

## CourtListener MCP lookups

- `search` type=d, court=scotus, docket_number=25-1070 — 0 results.
- `search` type=d, court=scotus, case_name="Mosaic Health" — 0 results.

## Web fetches

- https://www.supremecourt.gov/DocketPDF/25/25-1388/422758/20260902111200156_2026-09-01%20Final%20United%20Biologics%20cert%20reply.pdf — petitioner's reply brief (Sept. 2, 2026), on this docket and inside the snapshot; text extracted locally from the fetched PDF.
- https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/25-1070.html — docket of AstraZeneca Pharmaceuticals LP v. Mosaic Health, Inc., No. 25-1070: distributed for 5/14/2026, response requested 4/30/2026, BIO 7/22/2026, reply 8/4/2026, distributed for 9/28/2026, rescheduled 8/25/2026, redistributed 9/2/2026, CVSG 10/5/2026.

Nothing retrieved concerned this case's own disposition; the petition is pending with the SG's brief outstanding.
