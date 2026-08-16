# Retrieval log

Beyond the provisioned snapshot, documents, and the committed
`metrics/statpack.md`:

## CourtListener MCP

1. `search` (type `d`, court `scotus`, docket_number `25-1383`) — 0 results
   (SCOTUS dockets are thinly indexed in the search collection).
2. `call_endpoint` `dockets` (court `scotus`, docket_number `25-1383`) — found
   *Indian Harbor Insurance Company v. Town of Vinton, Louisiana*, docket id
   73500284, filed 2026-06-15, `date_terminated: null` (pending). This is the
   lead case this petition asks to be held for; its status is the decisive
   forward signal (disclosed in `flags.json`).
3. `call_endpoint` `docket-entries` (docket 73500284) — 0 results (no entry
   mirror for this SCOTUS docket).

## Corpus CLI

- `uv run fedcourts query --court scotus --era 2020s --disposition gvr --limit 5`
  — top priors included the *Monsanto v. Salas* / *Monsanto v. Johnson*
  companion petitions GVR'd 2026-06-30 (the hold-then-GVR pattern this
  petition invokes).
  `ranged corpus reads: 18 GET(s), 4718592 byte(s)`
- One earlier `fedcourts query --text ...` invocation failed (no such option)
  and read nothing.

No web searches. No lookup of this case's own docket or disposition beyond
the provisioned snapshot.
