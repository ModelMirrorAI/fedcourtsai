No corpus queries, CourtListener MCP lookups, or web searches were performed by this evaluator. Case facts were graded only from the provisioned event, outcome, blinded candidates, application, and docket snapshot. The committed statpack and output schemas were also read.

To check the base-rate build each candidate actually used, I ran:

- `UV_NO_SYNC=1 uv run fedcourts statpack-at data/cases/scotus/9526000698/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
- `UV_NO_SYNC=1 uv run fedcourts statpack-at data/cases/scotus/9526000698/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`

Both initial attempts stopped before reading history because the default uv cache path was read-only. Retrying each command with `UV_CACHE_DIR=/tmp/codex-evaluate-uv-cache` succeeded without installing packages. Both resolved build `7ea07eba62d321e1f52ef4712b1dfecf7cda8ede`, landed November 16, 2026 at 06:03:46 UTC, matching frozen digest `sha256:51adef9eb718f3df6423188358b9c32ada5eda492c113a279dca2a17bbba64c4`; alternative_sha was null. I read that build's statpack.json and interim/application-class section of statpack.md. These commands consult only local statpack history; no ranged corpus reads line applies. Scratch statpacks were written outside the tree as the contract permits.
