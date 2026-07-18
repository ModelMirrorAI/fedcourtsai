# Retrieval log — scotus/73500237 / evt-petition-disposition / claude-baseline / 20260718T064904Z

Forward-mode cell. Retrieval beyond the provisioned inputs:

## Corpus lookups (`fedcourts query`)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
   - stderr: `ranged corpus reads: 153 GET(s), 40108032 byte(s)`
   - Purpose: sample what recent granted petitions look like on the signal
     cuts. All sampled grants carried multiple conference distributions
     (relists), reinforcing the zero-relist down-weight for this case.
2. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 3`
   - stderr: `ranged corpus reads: 150 GET(s), 39321600 byte(s)`
   - Purpose: inspect the full field set on one prior row (e.g. Monsanto v.
     Salas, 24-1097: granted 2026-06-30 after 4 distributions).

Free-text/topic filtering is not available for SCOTUS rows (`--topic` is
circuit-only), so no subject-matter-targeted corpus retrieval was possible;
base rates came from the committed `metrics/statpack.md` and the per-fee-class
detail in `metrics/statpack.json` (paid Term-2025 grant rate ~5.4%).

## CourtListener MCP

None. The provisioned snapshot and full petition text (including the appended
Fourth Circuit and district-court opinions) covered the pre-decision record;
no live docket or opinion lookups were needed.

## Web searches

None.
