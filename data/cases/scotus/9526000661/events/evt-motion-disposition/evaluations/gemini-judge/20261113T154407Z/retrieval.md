# Evaluator Retrieval Log (`scotus/9526000661`, `evt-motion-disposition`, `gemini-judge`, `20261113T154407Z`)

No corpus queries (`fedcourts query` / `fedcourts open-events`), CourtListener MCP lookups, or web searches were performed beyond the provisioned cell inputs and committed `metrics/statpack.{md,json}`.

## Local CLI Verification

- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9526000661/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`
  - Resolved `build_sha: ca0c9e1a49e292692bdc5b092cd9f868561169b8` (`statpack_digest: sha256:9da7dbfa464075bfc7fab6e6b641ec9060684cd53259a76380a32823adf6f653`, shared by all three candidates) and confirmed via `diff -q` that it is byte-identical to the committed `metrics/statpack.json`.
- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts paths --court scotus --docket 9526000661 --event evt-motion-disposition --role evaluator`
  - Confirmed canonical cell paths (`case_id: scotus/9526000661`).
