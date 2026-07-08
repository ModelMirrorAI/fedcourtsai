# Retrieval log — scotus/1057937 / evt-petition-disposition

Beyond the provisioned snapshot and event definition, this run consulted:

## Committed base rates

- `metrics/statpack.md` — corpus-wide, by-court, and by-Term base rates. The
  "by era" and "Modern discretionary-cert petitions by disposition" sections
  referenced in `.github/prompts/predict.md` are absent from the committed
  file (flagged in `flags.json`).
- `metrics/statpack.json` — per-Term rows for 1990–1994 (OT1992: 12,581 cases,
  3 resolved, all `other` — too thin to use).

## Corpus lookups (`fedcourts` CLI, ranged backend)

- `fedcourts query --court scotus --era 1990s --limit 10`
  - `ranged corpus reads: 377 GET(s), 98566144 byte(s)`
  - Result: all ten priors are mislabeled — 19th-century state-court material
    carrying modern-looking docket numbers (e.g. 96-7185, 93-528) and
    `era: 1990s`. No usable era-matched priors; not relied on.
- The same query was re-run once to reformat the output compactly; its
  `ranged corpus reads` stderr line was not captured (same query, second
  transfer not recorded).

## Not consulted

- CourtListener MCP: not used.
- Web searches: none.
- The snapshot's associated opinion cluster (114669) was **deliberately not
  fetched** — for a decided historical docket it would disclose the realized
  disposition, which the contract forbids retrieving.
- Prior committed predictor output under `data/cases/scotus/1033955/` was read
  as a formatting/calibration reference (repo files, not external retrieval).
