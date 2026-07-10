# Retrieval log — claude-baseline / 20260710T181622Z

Mode: `forward` (pending petition; retrieval unrestricted). No `DECIDED_BEFORE`
clock set.

## Corpus lookups (`fedcourts` CLI, ranged reads against the remote)

1. `uv run fedcourts query --court scotus --era 2020s --limit 8`
   — `ranged corpus reads: 378 GET(s), 99090432 byte(s)`
   Sampled recently resolved 2020s SCOTUS petitions: 7 of 8 denied; the one
   grant (25-1223, Montoya Palacios) was a counseled federal immigration case.
2. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 6`
   — `ranged corpus reads: 109 GET(s), 28573696 byte(s)`
   Profile of recent grants: counseled, federal-question cases (immigration,
   federal agencies, employment), several with Solicitor General involvement.

## Base rates

- Committed `metrics/statpack.md`: resolved-SCOTUS row (granted 1.4%, denied
  4.4%, rest dismissed/other across all eras). The "Modern discretionary-cert
  petitions by disposition" section the predictor prompt anchors on is not
  present in the committed statpack (flagged in `flags.json`).

## CourtListener MCP

- **None — the CourtListener MCP server never became available in this cell**
  (the server did not finish connecting; no `mcp__courtlistener__*` tools were
  discoverable). Zero MCP calls were made. Proceeded on the provisioned inputs,
  the corpus CLI, and one web search.

## Web searches

1. Query: `"Francis" "Allstate" Georgia Court of Appeals A25D0341` — the
   Supreme Court of Georgia's published 2025 denial list
   (https://www.gasupreme.us/2025-denied/) confirms *Francis v. Allstate
   Insurance Co.* (A25D0341, S25D0137) was denied discretionary review. This
   concerns the lower-court history predating the event, not the (nonexistent)
   SCOTUS outcome.
