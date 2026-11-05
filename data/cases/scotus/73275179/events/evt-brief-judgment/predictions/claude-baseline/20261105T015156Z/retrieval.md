# Retrieval log

Provisioned inputs read: snapshot 2026-10-22.json, related/25-566.json, context.json, documents.json, questions-presented.txt, merits-brief-petitioner.txt, merits-brief-respondent.txt, merits-amicus-united-states.txt (summaries and selected passages). Base rates: `metrics/statpack.md` (merits docket and per-Justice votes sections).

Corpus lookups:
1. `uv run fedcourts query --court scotus --citation "597 U.S. 1" --citation "554 U.S. 570" --limit 5`
   — `ranged corpus reads: 10 GET(s), 2621440 byte(s)`; no rows. The note says only 200 SCOTUS rows carry citations.
2. `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5` — usage error (the help text printed); I re-issued it without `--era`.
3. `uv run fedcourts query --court scotus --disposition granted --limit 5`
   — `ranged corpus reads: 27 GET(s), 7077888 byte(s)`; returned recent unrelated grants (Scanlan, DOJ v. McNutt, FCC v. Brown, etc.). Not used.

No CourtListener MCP calls and no web searches.
