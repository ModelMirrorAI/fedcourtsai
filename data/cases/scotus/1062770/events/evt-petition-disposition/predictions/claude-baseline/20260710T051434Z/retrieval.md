# Retrieval log — claude-baseline / 20260710T051434Z

Beyond the provisioned inputs (event definition, snapshot, `AGENTS.md`, the
predict prompt, `schemas/prediction.schema.json`), I consulted:

1. `metrics/statpack.md` (committed base rates) — SCOTUS resolved base rate:
   other 78.4%, dismissed 15.9%, denied 4.4%, granted 1.4%. Note: the by-era
   and modern-discretionary-cert sections the predict prompt references are
   not present in the committed statpack.

2. `uv run fedcourts query --court scotus --era 1880s --corpus-backend ranged --limit 20`
   — returned no rows (no resolved 1880s SCOTUS priors surfaced).
   `ranged corpus reads: 378 GET(s), 99090432 byte(s)`

3. `uv run fedcourts query --court scotus --corpus-backend ranged --limit 20`
   — 20 resolved SCOTUS priors, captions empty in the compact rows; dispositions
   17× other, 3× dismissed, consistent with the statpack base rate.
   `ranged corpus reads: 378 GET(s), 99090432 byte(s)`

No CourtListener MCP lookups and no web searches. The opinion cluster linked in
the snapshot was deliberately **not** retrieved, since it would reveal this
case's own outcome.
