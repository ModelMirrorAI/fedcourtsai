# Retrieval log — claude-baseline / 20260710T234542Z

## Corpus lookups (`fedcourts`, ranged backend)

1. `uv run fedcourts query --court scotus --citation "579 U.S. 261" --citation "590 U.S. 45" --citation "584 U.S. 357" --corpus-backend ranged`
   — no matching priors returned.
   `ranged corpus reads: 378 GET(s), 99090432 byte(s)`
2. `uv run fedcourts query --court scotus --era 2020s --corpus-backend ranged`
   — 20 ranked resolved priors: 19 denied, 1 granted (~5% grant rate in the
   modern-era sample).
   `ranged corpus reads: 378 GET(s), 99090432 byte(s)`
3. Same query re-run to count the disposition split (same result set).
   `ranged corpus reads: 378 GET(s), 99090432 byte(s)`

## Committed base rates

- `metrics/statpack.md` — overall and per-court resolved base rates (scotus:
  granted 1.4% of resolved) and the by-Term table. The "modern
  discretionary-cert petitions by disposition" section referenced by the predict
  prompt is not present in the committed statpack (flagged in `flags.json`).

## CourtListener MCP

- Attempted `search` (Federal Circuit opinions on "settled expectations" IPR
  denials, to locate companion cases such as *In re Cambridge* / *In re SanDisk*
  and any parallel petitions): **server down** — both calls failed with
  `REDIS_URL is not set; cannot access session store.` No CourtListener data
  informed this prediction.

## Web searches

None.
