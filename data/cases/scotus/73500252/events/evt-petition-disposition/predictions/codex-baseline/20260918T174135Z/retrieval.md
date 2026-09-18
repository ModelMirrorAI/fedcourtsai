# Retrieval record

## Local inputs and reference material

- Read the governing `AGENTS.md`, `.github/prompts/predict.md`, and prediction, tooling, and flags schemas. Resolved the cell with `uv run fedcourts paths --court scotus --docket 73500252 --event evt-petition-disposition --role predictor`. The initial invocation could not initialize the default read-only uv cache; the same command succeeded with a temporary cache location.
- Read this cell's event, context, `record/snapshots/2026-09-17.json`, document manifest, questions presented, and relevant portions of the provisioned petition and opposition, including the lower opinion embedded in the petition. No target outcome, other prediction, or labeling artifact was read.
- Consulted `metrics/statpack.md`: modern cert disposition, originating-circuit, paid relist/CVSG cuts, and the sal-v4 per-Term band table. Consulted `metrics/statpack.json` for unrounded elevated-band reached rates and denominator counts for Terms 2017–2024. Computed the weighted pool locally: 484 / 2810 = 0.1722419929. No `fedcourts query` or `open-events` call; no ranged-corpus transfer line was produced.

## External retrieval

1. Web search: `site.supremecourt.gov opinions 2023 Cantero Bank America 22-529 2024`. The tool returned no content.
2. Web open: the Supreme Court's 2024 opinion PDF path `/opinions/23pdf/22-529_1b7d.pdf`. The tool returned no content. Neither unsuccessful web call supplied evidence.
3. CourtListener MCP `search`: type `o`, citation `602 U.S. 205`, filed before `2024-06-01`, one result requested, fields `caseName`, `dateFiled`, `citation`, `opinions`, `absolute_url`. Returned Cantero v. Bank of America, N. A., May 30, 2024, opinion ID 11066676. This is the earlier precedent, not the target petition's disposition.
4. CourtListener MCP `search_document`: opinion 11066676, literal query `practical assessment`, context 1,300 characters. Read the two returned excerpts confirming the comparative significant-interference framework, including the discussion at 219–220. No subsequent history was requested.

The opposition itself reports another petition's prior denial and pending rehearing in Conti. That provisioned, pre-snapshot companion history was used as context; it was not independently refreshed. No search sought the outcome of Flagstar's pending petition.
