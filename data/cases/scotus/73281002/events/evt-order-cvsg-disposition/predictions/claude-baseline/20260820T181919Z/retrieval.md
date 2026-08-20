# Retrieval log

Beyond the provisioned inputs (snapshot 2026-06-30, event.yaml, context.json,
questions-presented.txt, petition.txt, brief-in-opposition.txt,
documents.json) and the committed `metrics/statpack.md`:

## Corpus lookups

- `uv run fedcourts corpus-info` — **errored** (no local corpus blob in this
  cell; traceback out of `corpus.connect_readonly`). No transfer line.
- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
  — stderr: `ranged corpus reads: 31 GET(s), 8126464 byte(s)`. Used for
  modern granted priors; the useful row was RiseandShine Corp. v. PepsiCo
  (24-1016): CVSG 2025-10-06 → cert granted 2026-06-29, confirming the
  CVSG-to-grant timing pattern (~9 months) I forecast for this docket.

## CourtListener MCP lookups (forward mode — unrestricted)

- `search` (type=d, court=scotus, docket_number=25-967) — 0 results in the
  search index.
- `call_endpoint` (dockets, court=scotus, docket_number=25-967) — confirmed
  the vided companion: Pennsylvania v. Bette Eakin, docket id 73281009, filed
  2026-02-17.
- `call_endpoint` (dockets, id=73281002) — confirmed this docket is not
  terminated (`date_terminated: null`) as of prediction time; no disposition
  surfaced.

## Web searches

None.
