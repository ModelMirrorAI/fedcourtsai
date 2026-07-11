# Retrieval log — claude-baseline, run 20260710T234542Z

Beyond the provisioned inputs (snapshot, `record/documents/petition.txt`,
event definition, `record/context.json`), this cell consulted:

## Committed base rates

- `metrics/statpack.md` — overall and by-court disposition base rates, SCOTUS
  by-Term and by-originating-circuit cuts. Note: the "Modern
  discretionary-cert petitions by disposition" section referenced by
  `.github/prompts/predict.md` is not present in the committed statpack; the
  available SCOTUS cut (denied 4.4%, granted 1.4% of 296 resolved) blends
  merits-era labels.

## Corpus queries (`fedcourts query`, ranged backend)

- `uv run fedcourts query --court scotus --citation "392 U.S. 1" --citation
  "529 U.S. 266" --citation "550 U.S. 372" --corpus-backend ranged --limit 8`
  → 0 rows. Stderr: `ranged corpus reads: 378 GET(s), 99090432 byte(s)`
- `uv run fedcourts query --court scotus --citation "392 U.S. 1"
  --corpus-backend ranged --limit 5` → 0 rows. Stderr:
  `ranged corpus reads: 378 GET(s), 99090432 byte(s)`

No priors were returned; the resolved SCOTUS slice of the corpus is small and
citation-filtered retrieval found no overlap.

## CourtListener MCP (attempted, unavailable)

- `search` (opinions, q=`Rodriguez-Montes`, docket_number=`12-24-00161-CR`) →
  server error: `REDIS_URL is not set; cannot access session store.`
- `search` (opinions, q=`Rodriguez-Montes Terry frisk`, court=`texapp`) → same
  error.

The MCP server was down for this cell; no live CourtListener retrieval
informed the prediction. No web searches were performed.
