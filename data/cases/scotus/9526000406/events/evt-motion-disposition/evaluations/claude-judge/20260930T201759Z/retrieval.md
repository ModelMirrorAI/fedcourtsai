# Retrieval log (evaluator, claude-judge, run 20260930T201759Z)

No corpus, CourtListener, or web retrieval beyond the provisioned inputs.

- No `fedcourts query` / `fedcourts open-events` call was made, so no `ranged corpus reads` line to record.
- No CourtListener MCP lookup.
- No web search or fetch.

Local reads outside the cell's own directory, for the record:

- `metrics/statpack.md`, section *The interim docket (applications)*, to verify the pooled anchor (Terms 2024 and 2025: 31 granted / 296 resolved, 10.5%) that all three candidates quoted.
- `git log -1 -- metrics/statpack.md` (current pack `808f812e9`, 2026-09-28) and `git show 96ebdd342:metrics/statpack.md` (the pack the candidates cite): the 2024 and 2025 interim rows are identical across the two vintages.
- `record/documents/application.txt` and `record/snapshots/2026-09-29.json` (provisioned inputs) to check facts the candidates asserted and to read the disposing order.
