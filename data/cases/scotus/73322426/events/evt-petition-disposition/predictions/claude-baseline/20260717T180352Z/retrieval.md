# Retrieval log — scotus/73322426 / evt-petition-disposition / claude-baseline / 20260717T180352Z

Beyond the provisioned inputs (snapshot `2026-07-17.json`, `petition.txt`,
`questions-presented.txt`, `documents.json`, `event.yaml`, `context.json`
(mode: forward)):

## Committed base rates

- `metrics/statpack.md` and `metrics/statpack.json` — modern
  discretionary-cert base rates: Term 2025 overall grant ~2.5%, **paid**
  fee-class grant ~5.4% (IFP ~1.1%); relist-count cuts (0 relists → 0.8%
  granted, 2 relists → 33.6%); CVSG cut (not applicable here). No
  salience-band section exists in the committed statpack.

## Corpus lookups (`fedcourts`)

- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5`
  — stderr: `ranged corpus reads: 148 GET(s), 38666240 byte(s)`. Recent
  granted petitions for context on distribution counts and salience scores of
  grants (distribution_count 3–22 among the June 2026 grants returned).

## CourtListener MCP lookups

- `search(type=d, court=scotus, q="two-way video" confrontation,
  filed_after=2025-06-01)` — 0 results; no companion or competing SCOTUS
  petition on the same question surfaced.

No web searches were used. No information about this case's own disposition
was sought or encountered (the petition is pending; forward mode).
