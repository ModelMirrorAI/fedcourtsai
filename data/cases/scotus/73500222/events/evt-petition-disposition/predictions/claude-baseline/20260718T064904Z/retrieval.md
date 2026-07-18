# Retrieval log — scotus/73500222, evt-petition-disposition, claude-baseline, 20260718T064904Z

## Corpus tooling

- `uv run fedcourts query --court scotus --era 2020s --citation "144 S. Ct. 814" --limit 5`
  → failed: `corpus service at http://127.0.0.1:8377 is unreachable — is the sidecar running? (fedcourts corpus-serve): timed out`. No `ranged corpus reads:` line was printed (the call never reached the corpus).
- `uv run fedcourts query --court scotus --era 2020s --citation "142 S. Ct. 232" --limit 5`
  → same unreachable-sidecar failure, no transfer line.
- `uv run fedcourts open-events --court scotus --docket 73500222`
  → same unreachable-sidecar failure, no transfer line.

The corpus query sidecar was down for this cell, so no corpus priors could be
retrieved. Base-rate context came from the committed `metrics/statpack.md` and
`metrics/statpack.json` (modern discretionary-cert disposition split, per-Term
paid/IFP grant rates, relist-count and originating-circuit cuts) instead.

## CourtListener MCP

- `search(type=d, court=scotus, docket_number="25-1321")` → 0 results.
- `search(type=d, court=scotus, case_name="Karsjens")` → 0 results.

CourtListener's docket search index does not carry this SCOTUS docket; both
calls returned nothing and contributed no signal. No opinion, RECAP, or other
MCP lookups were made.

## Web searches

None.

Everything else came from the provisioned inputs: the 2026-07-18 snapshot, the
petition text, the questions-presented extract, and `documents.json`.
