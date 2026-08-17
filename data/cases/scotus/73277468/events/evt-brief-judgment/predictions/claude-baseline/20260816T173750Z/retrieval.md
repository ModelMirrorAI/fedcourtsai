# Retrieval log

Beyond the provisioned inputs (snapshot, event, context, and the three
provisioned document texts):

## Corpus lookups (`fedcourts query`, service backend)

1. `uv run fedcourts query --court scotus --citation "598 U.S. 729" --corpus-backend service`
   — 0 rows. stderr: `ranged corpus reads: 1329 GET(s), 348389376 byte(s)` and
   `note: citations filter: 161 of 590339 rows in scope (scotus) carry citation
   data, and the column holds a case's OWN reporter cites (not a
   cases-citing-this-authority graph) — an empty result here usually means
   missing data, not no match`.
2. `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5 --corpus-backend service`
   — 0 rows. stderr: `ranged corpus reads: 705 GET(s), 184811520 byte(s)`.

Neither query surfaced priors; no corpus-retrieved precedent informed this
prediction. Base rates came from the committed `metrics/statpack.md` (merits
docket section, pooled grant Terms 2017–2024).

## Web retrieval (forward mode — unrestricted)

3. Fetched the petitioner's merits brief (docket entry June 8, 2026) directly
   from the Supreme Court's docket:
   `https://www.supremecourt.gov/DocketPDF/25/25-352/412882/20260608170007524_25-352%20Brief.pdf`
   (66 pages; text extracted locally with pypdf). Read the summary of argument
   and argument headings.

## CourtListener MCP

None — the provisioned documents plus the fetched merits brief covered the
filings, and the docket snapshot was current to 2026-08-16.
