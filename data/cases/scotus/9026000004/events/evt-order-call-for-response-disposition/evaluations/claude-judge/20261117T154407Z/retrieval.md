# Retrieval log

No corpus query, CourtListener MCP lookup or web search.

Beyond the blinded candidates, the event and the outcome, I read these provisioned files to check candidates' record facts: `record/snapshots/2026-11-16.json` (docket entries, lower-court fields, counsel), `record/documents/petition.txt`, `questions-presented.txt`, `brief-in-opposition.txt` (grep and excerpts), `documents.json`, `record/context.json`.

Statpack rebuild, once per candidate:

- `uv run fedcourts statpack-at data/cases/scotus/9026000004/record/blinded/<alias>/ --ref origin/main --out-dir /tmp/statpack-at/<alias>` for gemini-baseline, -b and -c. Each resolved to build `7bcde3b105cb` (landed 2026-10-28, digest `sha256:84feb679...`), `alternative_sha` null. Candidates' base-rate figures were graded against that build, not the committed pack.
