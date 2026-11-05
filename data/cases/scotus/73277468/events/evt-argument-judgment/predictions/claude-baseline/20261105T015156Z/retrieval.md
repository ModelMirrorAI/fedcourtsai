# Retrieval

- Provisioned inputs: snapshot 2026-11-03.json, context.json, argument-features.json, documents/ (argument transcript, QP, merits briefs/reply, petition, BIO, cert reply).
- Committed statpack: `metrics/statpack.md`, sections "The merits docket (granted cases)" and "Per-Justice merits votes (complete lineups)".
- Corpus: `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5`. Refused with a usage message (the `--era modern` value was not accepted) and returned no rows.
- Corpus: `uv run fedcourts query --court scotus --disposition granted --limit 5`
  - stderr: `ranged corpus reads: 30 GET(s), 7864320 byte(s)`
  - Returned recent unrelated granted SCOTUS dockets (Scanlan, DOJ v. McNutt, FCC v. Brown, U.S. DOGE Service). None bore on this question, and none informed the forecast.
- No CourtListener MCP calls and no web searches.
