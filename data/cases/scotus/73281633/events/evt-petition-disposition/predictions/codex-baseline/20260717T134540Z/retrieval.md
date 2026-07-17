# Retrieval

## Corpus tooling

- `uv run fedcourts query --court scotus --topic 'commercial speech Central Hudson' --limit 5 --full`
  - The lookup failed because the ranged corpus backend could not resolve its storage endpoint. It emitted no `ranged corpus reads: ...` line and returned no priors.

## Base rates

- Consulted `metrics/statpack.md`, including modern discretionary-cert disposition rates and cuts by originating circuit, relist count, CVSG status, and Term.
- Consulted `metrics/statpack.json` for the 2025 Term paid-petition estimate.

## CourtListener MCP

- Searched SCOTUS opinions filed before July 17, 2026 for `"Central Hudson" evidence "common sense"`. The results surfaced the principal authorities already debated in the briefs, including *Rubin*, *Lorillard*, *Florida Bar*, and *44 Liquormart*.
- Searched SCOTUS opinions filed before July 17, 2026 for `"preliminary injunction" interlocutory certiorari`. The results provided general posture context but no close comparator that materially changed the forecast.

No web searches were used.
