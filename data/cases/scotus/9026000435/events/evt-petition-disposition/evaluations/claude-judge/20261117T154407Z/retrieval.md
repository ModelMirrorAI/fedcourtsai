# Retrieval log

No corpus query, CourtListener lookup or web search was made.

Beyond the provisioned inputs, one harness command was run per candidate to rebuild the statpack each was placed against:

- `uv run fedcourts statpack-at data/cases/scotus/9026000435/record/blinded/candidate-{a,b,c}/ --ref origin/main --out-dir /tmp/statpack-at/candidate-{a,b,c}`: all three resolved to build `7bcde3b105cb` (landed 2026-10-28, digest `sha256:84feb679…`), `alternative_sha` null. Base-rate figures were graded against that build, with the committed `metrics/statpack.md` read for comparison.

Also read: the provisioned `record/documents/petition.txt` (to check candidates' appendix citations) and `record/snapshots/2026-11-16.json`.
