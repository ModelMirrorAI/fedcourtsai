# Retrieval log — scotus/73275236 · evt-petition-disposition · claude-baseline · 20260713T190721Z

Cell mode: `forward` (retrieval unrestricted). No CourtListener MCP or REST
calls were needed — the provisioned snapshot was fetched the same day as this
run.

## Web fetch (supremecourt.gov, linked from the provisioned snapshot)

- `curl` of the May 18, 2026 filing
  `https://www.supremecourt.gov/DocketPDF/25/25-293/409180/20260518162619988_25-293%20-%20Letter%20re%20Dismissal.pdf`
  — purpose: read the letter behind the snapshot's final docket entry ("Hold
  Petition in Abeyance … submitted"). It disclosed the respondent's voluntary
  dismissal of the General Dynamics petitioners, settlements in principle with
  the remaining petitioners, and General Dynamics' stated intent to seek
  Munsingwear vacatur once the case is moot — the decisive input for this
  prediction.

## Corpus tooling

- `uv run fedcourts query --court scotus --citation "340 U.S. 36" --corpus-backend ranged`
  — purpose: find resolved priors citing *Munsingwear* for how such petitions
  were labeled. Returned no rows.
  Stderr: `ranged corpus reads: 408 GET(s), 106954752 byte(s)`

## Committed base rates

- `metrics/statpack.md` — "Modern discretionary-cert petitions by disposition"
  (anchor), "Cert petitions by CVSG status" (granted 28.3% for CVSG'd
  petitions), "Cert petitions by relist count", and the originating-circuit
  (ca4) cut.

## Repo code consulted (not case retrieval)

- `src/fedcourtsai/pipeline/cert_signals.py` — confirmed the outcome
  extractor's mapping: a GVR / grant-vacate-remand order labels **granted**;
  "petition dismissed" labels **dismissed** — needed to state the prediction in
  the same vocabulary the ground-truth label will use.
