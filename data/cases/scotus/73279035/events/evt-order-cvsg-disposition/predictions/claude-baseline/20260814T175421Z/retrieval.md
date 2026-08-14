# Retrieval log

Beyond the provisioned inputs (snapshot 2026-08-14, event.yaml,
record/context.json, questions-presented.txt, petition.txt,
brief-in-opposition.txt, documents.json) and the committed
`metrics/statpack.md`:

## Corpus

- `uv run fedcourts query --court scotus --citation "508 U.S. 248" --citation
  "534 U.S. 204" --citation "563 U.S. 421" --citation "577 U.S. 136" --limit 6`
  — lookup of the SCOTUS ERISA-remedies line (Mertens, Great-West, Amara,
  Montanile). Returned **no rows**; the tool printed its coverage note (161 of
  590,020 scotus-scope rows carry citation data).
  stderr: `ranged corpus reads: 1327 GET(s), 347865088 byte(s)`

## CourtListener MCP

- `search` (type `d`, court `scotus`, q "Rose v. PSA Airlines") — 0 results.
- `call_endpoint` `dockets` (court `scotus`, docket_number `23-734`) — found
  docket 72482680, Rose v. PSA Airlines, filed 2024-01-08.
- `call_endpoint` `docket-entries` (docket 72482680) — 0 entries in RECAP.

## Web searches

- "Rose v. PSA Airlines 23-734 Supreme Court solicitor general brief cert
  denied ERISA surcharge" — established cert was **denied April 15, 2024**,
  without a CVSG; the same § 502(a)(3) surcharge question, flagged there as an
  interlocutory vehicle. Sources: SCOTUSblog case page, natlawreview.com,
  erisalitigationadvisor.com.
- "Aldridge v. Regions Bank Supreme Court 25-590 solicitor general CVSG" —
  confirmed no SG brief filed and no disposition as of 2026-08-14 (docket
  state matches the provisioned snapshot); case background (Ruby Tuesday
  top-hat plans). Sources: SCOTUSblog case page, supremecourt.gov docket.

No search surfaced this case's own disposition (none exists — the petition is
pending the SG's brief). Nothing under `data/qp-topics/` was read.
