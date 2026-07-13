# Retrieval log — claude-baseline / 20260713T075800Z

Beyond the provisioned inputs (snapshot, event definition, context.json), this
cell consulted:

- **Committed statpack** (`metrics/statpack.md`) — SCOTUS base rates: the
  modern discretionary-cert disposition anchor and the TO2025 Term row.
- **Corpus priors** via `fedcourts query`:
  - `uv run fedcourts query --court scotus --disposition granted --corpus-backend ranged --limit 5`
  - stderr: `ranged corpus reads: 129 GET(s), 33816576 byte(s)`
  - Purpose: see how petition-stage grants are recorded in the corpus and skim
    recent granted priors. The results (generic recent grants) did not
    materially move the estimate.

**No CourtListener MCP calls and no REST fallback calls were made.** This was
deliberate: the provisioned snapshot already revealed that the case has been
decided (see `flags.json`), so any further retrieval about this case could only
compound outcome exposure. No web searches were run.
