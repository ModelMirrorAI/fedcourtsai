# Retrieval log

- CourtListener MCP `search` (type=o, court=scotus, case_name="Pitchford v. Cain") → 1 result: Pitchford v. Cain, No. 24-7351, filed 2026-05-28. Used to confirm Pitchford postdates the decision below.
- `uv run fedcourts query --court scotus --disposition gvr --era modern` → usage error (era must be a decade token); no rows.
- `uv run fedcourts query --court scotus --disposition gvr --era 2020s --limit 5` → `ranged corpus reads: 37 GET(s), 9699328 byte(s)`; 5 recent GVR priors (e.g. Cid v. United States). Context only; none on this question.
- `uv run fedcourts query --docket-number 24-7351` → usage error (needs --court); no rows.
- Read committed `metrics/statpack.md` (modern cert, relist, CVSG, amicus, salience band tables).
