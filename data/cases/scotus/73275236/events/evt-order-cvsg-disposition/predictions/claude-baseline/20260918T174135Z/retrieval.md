# Retrieval log

## Corpus tooling

- `uv run fedcourts query --court scotus --era 2020s --disposition granted`
  — stderr: `ranged corpus reads: 47 GET(s), 12320768 byte(s)`. Returned recent
  OT2025 grants, mostly interim applications plus a few cert grants; used only as a
  sanity check on the corpus's recent grant shapes, not as case-matched priors.
- `uv run fedcourts query --court scotus --era 2020s --disposition denied`
  — stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm cache). Same use.
- `metrics/statpack.md` (committed): modern-cert base rate, CVSG cut, relist cut,
  salience band cut, and the sal-v4 "Segment base rate by salience band" table
  (pooled `high` bracketed `reached` rate over OT2017–OT2024).

## CourtListener MCP

- `call_endpoint` `docket-entries` with `docket=73275236` → 0 results (SCOTUS
  dockets carry no RECAP entries).
- `get_endpoint_item` `dockets/73275236` → case name, docket number 25-293,
  `date_filed` 2025-09-15, `date_terminated` null, `date_cert_granted` null,
  `date_cert_denied` null, `date_modified` 2026-05-18.

## Web fetches (forward-mode docket state)

- `https://www.supremecourt.gov/docket/docketfiles/html/public/25-293.html` (twice,
  different prompts) — full Proceedings and Orders table; last entry May 18, 2026,
  "Hold Petition in Abeyance of General Dynamics Corp., et al. submitted."; no SG
  brief, no order on the petition.
- `https://www.supremecourt.gov/DocketPDF/25/25-293/409180/20260518162619988_25-293%20-%20Letter%20re%20Dismissal.pdf`
  — petitioners' May 18, 2026 letter (text extracted locally with pypdf after the
  fetch tool could not parse it).
- `https://www.law360.com/articles/2469809/shipbuilders-lose-bid-to-block-new-plaintiff-in-no-poach-suit`
  — April 24, 2026; EDVA allowed a new plaintiff to join (paywalled; headline and
  lede only).
- `https://www.cohenmilstein.com/shipbuilders-cut-deals-to-end-no-poach-claims/`
  — March 19, 2026; Huntington Ingalls, Marinette Marine and Serco affiliates
  settled, terms undisclosed.

## Web searches

- "Scharpf General Dynamics naval engineers no-poach settlement 2026 Supreme Court petition"
- "shipbuilders no-poach class action settlement Scharpf Huntington Ingalls General Dynamics 2026"

None of the above surfaced a disposition of the petition; the docket shows it
undecided.
