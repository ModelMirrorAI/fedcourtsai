# Retrieval log

Beyond the provisioned inputs (snapshot `2026-08-14.json`, `petition.txt`,
`questions-presented.txt`, `documents.json`, `record/context.json`,
`event.yaml`) and the committed `metrics/statpack.md`:

## CourtListener MCP lookups (forward mode, unrestricted)

1. `search` (type `o`, court `ca5`, q "Endure Industries Vizient") — found the
   single published Fifth Circuit opinion, *Endure Industries v. Vizient*,
   No. 24-10995, filed 2026-01-13 (opinion id 10773935). Purpose: check for a
   dissent below and panel composition.
2. `get_endpoint_item` (opinions/10773935) — returned `cluster_id` 10307347,
   no author string, 13 pages.
3. `get_endpoint_item` (clusters/10307347) — returned metadata for a
   **different case** (*Franklin v. Austal USA, LLC*, 2025-01-03), so the
   panel/separate-opinion check was inconclusive. Treated as a CourtListener
   data inconsistency; no further calls spent on it.

No web searches. Nothing outcome-revealing surfaced (the petition is pending;
forward cell).

## Corpus lookups

None — no `fedcourts query` / `open-events` calls this run. The statpack's
modern-cert, relist, CVSG, circuit, and salience-band sections covered the
base-rate needs, and the corpus carries no topical filter on SCOTUS rows that
would surface antitrust-specific priors.
