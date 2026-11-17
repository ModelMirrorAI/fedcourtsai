# Evaluator Retrieval Log (`scotus/73377829` — `evt-order-call-for-response-disposition`)

No corpus queries (`uv run fedcourts query` / `open-events`), CourtListener MCP lookups, or web searches were executed beyond the provisioned inputs.

To verify the candidates' base-rate citations against the statpack build in force at their prediction run (`20261029T142045Z`), reconstructed that historical statpack locally from `origin/main`:

- `uv run fedcourts statpack-at data/cases/scotus/73377829/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline` -> `7bcde3b105cb` (`sha256:84feb6798b6407fea2a17fed92c36d8a8db71d12850a967d840f018295ba4641`)
- `uv run fedcourts statpack-at data/cases/scotus/73377829/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline` -> `7bcde3b105cb` (`sha256:84feb6798b6407fea2a17fed92c36d8a8db71d12850a967d840f018295ba4641`)
- `uv run fedcourts statpack-at data/cases/scotus/73377829/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline` -> `7bcde3b105cb` (`sha256:84feb6798b6407fea2a17fed92c36d8a8db71d12850a967d840f018295ba4641`)
