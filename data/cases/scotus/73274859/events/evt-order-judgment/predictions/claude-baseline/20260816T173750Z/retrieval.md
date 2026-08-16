# Retrieval log — claude-baseline, scotus/73274859, evt-order-judgment, 20260816T173750Z

Beyond the provisioned inputs (snapshot, event.yaml, context.json,
questions-presented.txt, petition.txt, brief-in-opposition.txt — the last
containing both the Nov 2025 BIO and the Jul 2026 respondents' merits brief)
and the committed `metrics/statpack.md`:

## Corpus lookups

- `uv run fedcourts query --court scotus --citation "564 U.S. 410" --limit 3`
  (known-case lookup for AEP v. Connecticut as a prior) — returned no rows.
  - `ranged corpus reads: 1329 GET(s), 348389376 byte(s)`
  - The CLI's own note: the citation column covers 161 of 590,339 SCOTUS rows,
    so the empty result reflects coverage, not absence. Per the sparse-filter
    guidance I did not retry.

## CourtListener MCP

None.

## Web searches

None.
