# Retrieval log — scotus/73369988, run 20260718T000130Z

Beyond the provisioned inputs (snapshot, questions-presented.txt, petition.txt)
and the committed `metrics/statpack.md` / `metrics/statpack.json`:

1. `uv run fedcourts query --court scotus --era 2020s --limit 5`
   - stderr: `ranged corpus reads: 431 GET(s), 112852992 byte(s)`
   - Returned 5 recent resolved SCOTUS priors (generic, not
     arbitration-specific — the query surface takes structured filters only, so
     I could not target evident-partiality/arbitration subject matter; the
     priors did not move the estimate and the statpack base rates carried the
     quantitative anchoring).

No CourtListener MCP lookups and no web searches were used: the provisioned
petition text was complete (29 pages, not truncated), the respondent waived a
response so no BIO exists to fetch, and the deny signals were unambiguous
without further retrieval.

(One `fedcourts query` attempt with an unsupported `--text` option errored
before reaching the corpus and performed no reads; `--help` invocations are
omitted as they read nothing.)
