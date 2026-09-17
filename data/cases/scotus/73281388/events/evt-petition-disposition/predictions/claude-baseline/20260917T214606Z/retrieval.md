# Retrieval log

Provisioned inputs read: `record/snapshots/2026-09-17.json`, `record/context.json`,
`record/documents/documents.json`, `questions-presented.txt`, `petition.txt`,
`brief-in-opposition.txt`, the event's `event.yaml`, `metrics/statpack.md`.

## Corpus lookups (`fedcourts`)

- `uv run fedcourts paths --court scotus --docket 73281388 --event evt-petition-disposition --role predictor`
  (path resolution; no transfer line).
- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
  stderr: `ranged corpus reads: 28 GET(s), 7340032 byte(s)`. Returned eight
  recent granted rows (mostly OT2025 emergency applications and a few paid
  petitions); used only as a sanity check on the corpus surface, not as
  case-specific priors. No filter reaches the feature that matters here (a
  call for response), so no further queries.
- An earlier invocation with a mis-typed flag value (`--include-open false`)
  errored on argument parsing and read nothing.

## Web fetches (forward mode, unrestricted)

- `https://www.supremecourt.gov/DocketPDF/25/25-1105/423591/20260909155307313_Thompson%20Supp%20Brief%20Final%20pdfa.pdf`
  (petitioner's supplemental brief, Sept. 9, 2026; PDF fetched via WebFetch,
  text extracted locally). Raises *Richards v. Newsom*, No. 25-693 (9th Cir.
  Aug. 27, 2026).
- `https://www.supremecourt.gov/DocketPDF/25/25-1105/416882/20260720141830581_Thompson%20Reply%20FINAL%20PDFA%207-20-26.pdf`
  (petitioner's reply, July 20, 2026; same method).

Both are this docket's own filings, linked from the provisioned snapshot and
predating it; neither is outcome material.

## CourtListener MCP

- `search` type=`o`, court=`scotus`, q=`Chatrie geofence`, filed_after
  2025-10-01: one result, *Chatrie v. United States*, No. 25-112, filed
  2026-06-29, published. Used only to establish that the case the petition
  cites as pending has been decided; the opinion was not read.

No search for this case's own disposition was run; the petition is on the
September 28, 2026 conference list per the snapshot and is undecided.
