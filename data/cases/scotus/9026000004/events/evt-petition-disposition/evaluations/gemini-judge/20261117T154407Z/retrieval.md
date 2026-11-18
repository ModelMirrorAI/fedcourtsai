# Evaluator Retrieval Log

## Corpus CLI Queries (`uv run fedcourts query`)

1. `uv run fedcourts query --court scotus --docket-number 21-926`
   - `ranged corpus reads: 21 GET(s), 5505024 byte(s)`
   - Verified *Cooper Tire & Rubber Company v. Tyrance McCall* (`scotus/72475093`), `disposition: denied`, `date_decided: 2023-06-30`, `distribution_count: 4`.
2. `uv run fedcourts query --court scotus --docket-number 24-1190`
   - `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Verified *Syngenta Crop Protections, LLC, et al. v. Douglas Nemeth, et al.* (`scotus/72483675`), `disposition: denied`, `date_decided: 2025-10-06`, `distribution_count: 1`.
3. `uv run fedcourts query --court scotus --docket-number 25-1208`
   - `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Verified *Norfolk Southern Railway Company v. Robert Willmore Mallory, et al.* (`scotus/73281694`), `disposition: denied`, `date_decided: 2026-10-05`, `distribution_count: 2`.

## Statpack History Reconstruction (`uv run fedcourts statpack-at`)

- `uv run fedcourts statpack-at data/cases/scotus/9026000004/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
- `uv run fedcourts statpack-at data/cases/scotus/9026000004/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`
- `uv run fedcourts statpack-at data/cases/scotus/9026000004/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`
  - All three candidates resolved to `build_sha: 7bcde3b105cb212283905eda17b827efc188e80c` (`digest: sha256:84feb6798b6407fea2a17fed92c36d8a8db71d12850a967d840f018295ba4641`, `sal-v4`, landed `2026-10-28T13:56:30-04:00`).

## CourtListener MCP & Web Searches

- No CourtListener MCP lookups and no web searches.
