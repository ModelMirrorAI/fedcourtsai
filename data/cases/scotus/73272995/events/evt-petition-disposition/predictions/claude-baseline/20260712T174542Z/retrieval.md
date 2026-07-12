# Retrieval log — scotus/73272995 / evt-petition-disposition / claude-baseline / 20260712T174542Z

Beyond the provisioned inputs (snapshot, event definition, petition.txt,
questions-presented.txt, documents.json, context.json), I consulted:

## Committed base rates

- `metrics/statpack.md` — "Modern discretionary-cert petitions by disposition"
  anchor (Term 2025: denied 92.6%, granted 4.9%, dismissed 2.5%) and the
  per-Term table.
- `metrics/statpack.json` — per-fee-class detail for Term 2025: paid
  est. grant rate 7.2%; IFP 62 resolved, 0 granted (96.8% denied, 3.2%
  dismissed).

## Corpus lookups (`fedcourts` CLI, ranged backend)

- `uv run fedcourts query --court scotus --era 2020s --disposition dismissed --corpus-backend ranged --limit 5`
  — profile of petitions the corpus labels "dismissed" (procedural
  terminations, mostly pro se), to choose between the dismissed/denied labels.
  Stderr: `ranged corpus reads: 214 GET(s), 56098816 byte(s)`

## CourtListener MCP / REST

None. The cell is forward-mode with unrestricted retrieval, but the
provisioned snapshot already carried the docket through its final entry
("Case considered closed", Jan 15 2026 — see flags.json), so no external
lookup could add forward signal, and the predict-as-if-undecided rule
forbids seeking anything more about this case's disposition. No MCP calls,
no REST fallback, no web searches.
